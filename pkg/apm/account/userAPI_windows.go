package account

import (
	"errors"
	"fmt"
	"os"
	"syscall"
	"time"
	"unsafe"
)

var (
	modNetapi32                = syscall.NewLazyDLL("netapi32.dll")
	modAdvapi32                = syscall.NewLazyDLL("advapi32.dll")
	modKerapi32                = syscall.NewLazyDLL("kernel32.dll")
	usrNetUserEnum             = modNetapi32.NewProc("NetUserEnum")
	usrNetUserAdd              = modNetapi32.NewProc("NetUserAdd")
	usrNetUserDel              = modNetapi32.NewProc("NetUserDel")
	usrNetGetAnyDCName         = modNetapi32.NewProc("NetGetAnyDCName")
	usrNetUserGetInfo          = modNetapi32.NewProc("NetUserGetInfo")
	usrNetUserSetInfo          = modNetapi32.NewProc("NetUserSetInfo")
	usrNetLocalGroupAddMembers = modNetapi32.NewProc("NetLocalGroupAddMembers")
	usrNetLocalGroupDelMembers = modNetapi32.NewProc("NetLocalGroupDelMembers")
	usrNetLocalGroupGetMembers = modNetapi32.NewProc("NetLocalGroupGetMembers")
	usrNetApiBufferFree        = modNetapi32.NewProc("NetApiBufferFree")
	groupNetLocalGroupAdd      = modNetapi32.NewProc("NetLocalGroupAdd")
	groupNetLocalGroupDel      = modNetapi32.NewProc("NetLocalGroupDel")
	groupNetLocalGroupEnum     = modNetapi32.NewProc("NetLocalGroupEnum")

	advLsaOpenPolicy             = modAdvapi32.NewProc("LsaOpenPolicy")
	advLsaAddAccountRights       = modAdvapi32.NewProc("LsaAddAccountRights")
	advLsaRemoveAccountRights    = modAdvapi32.NewProc("LsaRemoveAccountRights")
	advLsaEnumerateAccountRights = modAdvapi32.NewProc("LsaEnumerateAccountRights")
	advLsaClose                  = modAdvapi32.NewProc("LsaClose")
	advLookupAccountName         = modAdvapi32.NewProc("LookupAccountNameW")
	advLookupPrivilegeValue      = modAdvapi32.NewProc("LookupPrivilegeValueW")
	advAdjustTokenPrivileges     = modAdvapi32.NewProc("AdjustTokenPrivileges")
	advDuplicateTokenEx          = modAdvapi32.NewProc("DuplicateTokenEx")
	advImpersonateLoggedOnUser   = modAdvapi32.NewProc("ImpersonateLoggedOnUser")
	advRevertToSelf              = modAdvapi32.NewProc("RevertToSelf")
	advLsaFreeMemory             = modAdvapi32.NewProc("LsaFreeMemory")
	// logon
	advLogonUser = modAdvapi32.NewProc("LogonUserW")
	// get last error
	kerGetLastError = modKerapi32.NewProc("GetLastError")
)

const (
	STATUS_SUCCESS                                   = 0
	NET_API_STATUS_NERR_Success                      = 0
	NET_API_STATUS_NERR_InvalidComputer              = 2351
	NET_API_STATUS_NERR_NotPrimary                   = 2226
	NET_API_STATUS_NERR_SpeGroupOp                   = 2234
	NET_API_STATUS_NERR_LastAdmin                    = 2452
	NET_API_STATUS_NERR_BadPassword                  = 2203
	NET_API_STATUS_NERR_PasswordTooShort             = 2245
	NET_API_STATUS_NERR_UserNotFound                 = 2221
	NET_API_STATUS_ERROR_ACCESS_DENIED               = 5
	NET_API_STATUS_ERROR_NOT_ENOUGH_MEMORY           = 8
	NET_API_STATUS_ERROR_INVALID_PARAMETER           = 87
	NET_API_STATUS_ERROR_INVALID_NAME                = 123
	NET_API_STATUS_ERROR_INVALID_LEVEL               = 124
	NET_API_STATUS_ERROR_MORE_DATA                   = 234
	NET_API_STATUS_ERROR_SESSION_CREDENTIAL_CONFLICT = 1219
	NET_API_STATUS_RPC_S_SERVER_UNAVAILABLE          = 2147944122
	NET_API_STATUS_RPC_E_REMOTE_DISABLED             = 2147549468

	USER_PRIV_MASK  = 0x3
	USER_PRIV_GUEST = 0
	USER_PRIV_USER  = 1
	USER_PRIV_ADMIN = 2

	USER_FILTER_NORMAL_ACCOUNT = 0x0002
	USER_MAX_PREFERRED_LENGTH  = 0xFFFFFFFF

	USER_UF_SCRIPT             = 1
	USER_UF_ACCOUNTDISABLE     = 2
	USER_UF_LOCKOUT            = 16
	USER_UF_PASSWD_CANT_CHANGE = 64
	USER_UF_NORMAL_ACCOUNT     = 512
	USER_UF_DONT_EXPIRE_PASSWD = 65536

	LOGON32_LOGON_INTERACTIVE = 2
	LOGON32_LOGON_NETWORK     = 3
	LOGON32_LOGON_BATCH       = 4
	LOGON32_LOGON_SERVICE     = 5
	LOGON32_PROVIDER_DEFAULT  = 0

	// LSA policy
	POLICY_VIEW_LOCAL_INFORMATION   = 0x00000001
	POLICY_VIEW_AUDIT_INFORMATION   = 0x00000002
	POLICY_GET_PRIVATE_INFORMATION  = 0x00000004
	POLICY_TRUST_ADMIN              = 0x00000008
	POLICY_CREATE_ACCOUNT           = 0x00000010
	POLICY_CREATE_SECRET            = 0x00000020
	POLICY_CREATE_PRIVILEGE         = 0x00000040
	POLICY_SET_DEFAULT_QUOTA_LIMITS = 0x00000080
	POLICY_SET_AUDIT_REQUIREMENTS   = 0x00000100
	POLICY_AUDIT_LOG_ADMIN          = 0x00000200
	POLICY_SERVER_ADMIN             = 0x00000400
	POLICY_LOOKUP_NAMES             = 0x00000800
	POLICY_NOTIFICATION             = 0x00001000
	READ_CONTROL                    = 0x00020000
	STANDARD_RIGHTS_READ            = READ_CONTROL
	STANDARD_RIGHTS_WRITE           = READ_CONTROL
	STANDARD_RIGHTS_EXECUTE         = READ_CONTROL
	POLICY_ALL_ACCESS               = 0x000f0fff

	GENERIC_ALL_ACCESS   = 0x10000000
	SE_PRIVILEGE_ENABLED = 0x00000002
	SE_PRIVILEGE_REMOVED = 0x00000004

	// token priv
	TOKEN_ASSIGN_PRIMARY = 0x00000001
	TOKEN_ALL_ACCESS     = 0x000f01ff
	// duplicate key level
	SecurityAnonymous      = 0
	SecurityIdentification = 1
	SecurityImpersonation  = 2
	SecurityDelegation     = 3
	// token type
	TokenPrimary = 1
)

// types
type (
	LSA_HANDLE uintptr
	SID        []byte
)

// structs
type GROUP_USERS_INFO_0 struct {
	grui0_name *uint16
}

type USER_INFO_1 struct {
	Usri1_name         *uint16
	Usri1_password     *uint16
	Usri1_password_age uint32
	Usri1_priv         uint32
	Usri1_home_dir     *uint16
	Usri1_comment      *uint16
	Usri1_flags        uint32
	Usri1_script_path  *uint16
}

type USER_INFO_2 struct {
	Usri2_name           *uint16
	Usri2_password       *uint16
	Usri2_password_age   uint32
	Usri2_priv           uint32
	Usri2_home_dir       *uint16
	Usri2_comment        *uint16
	Usri2_flags          uint32
	Usri2_script_path    *uint16
	Usri2_auth_flags     uint32
	Usri2_full_name      *uint16
	Usri2_usr_comment    *uint16
	Usri2_parms          *uint16
	Usri2_workstations   *uint16
	Usri2_last_logon     uint32
	Usri2_last_logoff    uint32
	Usri2_acct_expires   uint32
	Usri2_max_storage    uint32
	Usri2_units_per_week uint32
	Usri2_logon_hours    uintptr
	Usri2_bad_pw_count   uint32
	Usri2_num_logons     uint32
	Usri2_logon_server   *uint16
	Usri2_country_code   uint32
	Usri2_code_page      uint32
}

type USER_INFO_1003 struct {
	Usri1003_password *uint16
}

type USER_INFO_1008 struct {
	Usri1008_flags uint32
}

type USER_INFO_1011 struct {
	Usri1011_full_name *uint16
}

type LOCALGROUP_INFO_1 struct {
	lgrpi1_name    *uint16
	lgrpi1_comment *uint16
}

type LOCALGROUP_MEMBERS_INFO_1 struct {
	lgrmi1_sid      *byte
	lgrmi1_sidusage int
	lgrmi1_name     *uint16
}

type LOCALGROUP_MEMBERS_INFO_3 struct {
	Lgrmi3_domainandname *uint16
}

type LSA_UNICODE_STRING struct {
	Length        uint16
	MaximumLength uint16
	Buffer        *uint16
}

type LSA_OBJECT_ATTRIBUTES struct {
	Length                   uint64
	RootDirectory            uintptr
	ObjectName               *LSA_UNICODE_STRING
	Attributes               uint64
	SecurityDescriptor       unsafe.Pointer
	SecurityQualityOfService unsafe.Pointer
}

type LSA_TRANSLATED_SID struct {
	Use         int64
	RelativeId  uint64
	DomainIndex int64
}

type LUID struct {
	LowPart  uint32
	HighPart int64
}

type LUID_AND_ATTRIBUTES struct {
	Luid       LUID
	Attributes uint32
}

type TOKEN_PRIVILEGES struct {
	PrivilegeCount uint32
	Privileges     LUID_AND_ATTRIBUTES
}

type SECURITY_ATTRIBUTES struct {
	nLength              uint32
	lpSecurityDescriptor *uint16
	bInheritHandle       int
}

// LocalUser -type
type LocalUser struct {
	Username             string
	FullName             string
	IsEnabled            bool
	IsLocked             bool
	IsAdmin              bool
	PasswordNeverExpires bool
	NoChangePassword     bool
	PasswordAge          time.Duration
	LastLogon            time.Time
	BadPasswordCount     uint32
	NumberOfLogons       uint32
}

// logonUser - logon user
func logonUser(username string, password string) (uintptr, error) {

	uPointer, err := syscall.UTF16PtrFromString(username)
	if err != nil {
		return 0, fmt.Errorf("Unable to encode username to UTF16")
	}
	pPointer, err := syscall.UTF16PtrFromString(password)
	if err != nil {
		return 0, fmt.Errorf("Unable to encode password to UTF16")
	}

	qPointer, _ := syscall.UTF16PtrFromString(".")

	var token uintptr
	ret, _, lastErr := advLogonUser.Call(
		uintptr(unsafe.Pointer(uPointer)),
		uintptr(unsafe.Pointer(qPointer)),
		uintptr(unsafe.Pointer(pPointer)),
		LOGON32_LOGON_BATCH,
		LOGON32_PROVIDER_DEFAULT,
		uintptr(unsafe.Pointer(&token)),
	)

	if ret == 0 {
		return 0, lastErr
	}

	return token, nil
}

// User Accounts API
// List:
//
// userAdd(username, fullname, password) (bool, error)
// userDelete(username) (bool, error)
// listUsers() ([]LocalUser, error)
// addGroupMembership(username, groupname) (bool, error)
// removeGroupMembership(username, groupname) (bool, error)
// userUpdateFullname(username, fullname) (bool, error)
// userDisabled(username string, disable bool) (bool, error)
// userPasswordNoExpires(username string, noexpire bool) (bool, error)
// userDisablePasswordChange(username string, disabled bool) (bool, error)
// userGetFlags(username string) (uint32, error)
// userSetFlags(username string, flags uint32) (bool, error)
// userAddFlags(username string, flags uint32) (bool, error)
// userDelFlags(username string, flags uint32) (bool, error)

func userAdd(username string, fullname string, password string, groupname string) (bool, error) {
	var parmErr uint32
	uPointer, err := syscall.UTF16PtrFromString(username)
	if err != nil {
		return false, fmt.Errorf("Unable to encode username to UTF16")
	}
	pPointer, err := syscall.UTF16PtrFromString(password)
	if err != nil {
		return false, fmt.Errorf("Unable to encode password to UTF16")
	}
	uInfo := USER_INFO_1{
		Usri1_name:     uPointer,
		Usri1_password: pPointer,
		Usri1_priv:     USER_PRIV_USER,
		Usri1_flags:    USER_UF_SCRIPT | USER_UF_NORMAL_ACCOUNT | USER_UF_DONT_EXPIRE_PASSWD,
	}
	ret, _, _ := usrNetUserAdd.Call(
		uintptr(0),
		uintptr(uint32(1)),
		uintptr(unsafe.Pointer(&uInfo)),
		uintptr(unsafe.Pointer(&parmErr)),
	)
	if ret != NET_API_STATUS_NERR_Success {
		return false, fmt.Errorf("Unable to process. %d %d", ret, parmErr)
	}
	if ok, err := userUpdateFullname(username, fullname); err != nil {
		return false, fmt.Errorf("While setting Full Name. %s", err.Error())
	} else if !ok {
		return false, fmt.Errorf("Problem while setting Full Name")
	}

	return addGroupMembership(username, groupname)
}

func userDelete(username string) (bool, error) {
	uPointer, err := syscall.UTF16PtrFromString(username)
	if err != nil {
		return false, fmt.Errorf("Unable to encode username to UTF16")
	}
	ret, _, _ := usrNetUserDel.Call(
		uintptr(0),
		uintptr(unsafe.Pointer(uPointer)),
	)
	if ret != NET_API_STATUS_NERR_Success {
		return false, fmt.Errorf("Unable to process. %d", ret)
	}
	return true, nil
}

func listUsers() ([]LocalUser, error) {
	var (
		dataPointer  uintptr
		resumeHandle uintptr
		entriesRead  uint32
		entriesTotal uint32
		sizeTest     USER_INFO_2
	)

	retVal := make([]LocalUser, 0)

	ret, _, _ := usrNetUserEnum.Call(
		uintptr(0),                                  // servername
		uintptr(uint32(2)),                          // level, USER_INFO_2
		uintptr(uint32(USER_FILTER_NORMAL_ACCOUNT)), // filter, only "normal" accounts.
		uintptr(unsafe.Pointer(&dataPointer)),       // struct buffer for output data.
		uintptr(uint32(USER_MAX_PREFERRED_LENGTH)),  // allow as much memory as required.
		uintptr(unsafe.Pointer(&entriesRead)),
		uintptr(unsafe.Pointer(&entriesTotal)),
		uintptr(unsafe.Pointer(&resumeHandle)),
	)
	if ret != NET_API_STATUS_NERR_Success {
		return nil, fmt.Errorf("Error fetching user entry")
	} else if dataPointer == uintptr(0) {
		return nil, fmt.Errorf("Null pointer while fetching entry")
	}

	var iter = dataPointer
	for i := uint32(0); i < entriesRead; i++ {
		var data = (*USER_INFO_2)(unsafe.Pointer(iter))

		ud := LocalUser{
			Username:         utf16toString(data.Usri2_name),
			FullName:         utf16toString(data.Usri2_full_name),
			PasswordAge:      (time.Duration(data.Usri2_password_age) * time.Second),
			LastLogon:        time.Unix(int64(data.Usri2_last_logon), 0),
			BadPasswordCount: data.Usri2_bad_pw_count,
			NumberOfLogons:   data.Usri2_num_logons,
		}

		if (data.Usri2_flags & USER_UF_ACCOUNTDISABLE) != USER_UF_ACCOUNTDISABLE {
			ud.IsEnabled = true
		}
		if (data.Usri2_flags & USER_UF_LOCKOUT) == USER_UF_LOCKOUT {
			ud.IsLocked = true
		}
		if (data.Usri2_flags & USER_UF_PASSWD_CANT_CHANGE) == USER_UF_PASSWD_CANT_CHANGE {
			ud.NoChangePassword = true
		}
		if (data.Usri2_flags & USER_UF_DONT_EXPIRE_PASSWD) == USER_UF_DONT_EXPIRE_PASSWD {
			ud.PasswordNeverExpires = true
		}
		if data.Usri2_priv == USER_PRIV_ADMIN {
			ud.IsAdmin = true
		}

		retVal = append(retVal, ud)

		iter = uintptr(unsafe.Pointer(iter + unsafe.Sizeof(sizeTest)))
	}
	_, _, _ = usrNetApiBufferFree.Call(uintptr(unsafe.Pointer(dataPointer)))
	return retVal, nil
}

func addGroupMembership(username, groupname string) (bool, error) {
	hn, _ := os.Hostname()
	uPointer, err := syscall.UTF16PtrFromString(hn + `\` + username)
	if err != nil {
		return false, fmt.Errorf("Unable to encode username to UTF16")
	}
	gPointer, err := syscall.UTF16PtrFromString(groupname)
	if err != nil {
		return false, fmt.Errorf("Unable to encode group name to UTF16")
	}
	var uArray = make([]LOCALGROUP_MEMBERS_INFO_3, 1)
	uArray[0] = LOCALGROUP_MEMBERS_INFO_3{
		Lgrmi3_domainandname: uPointer,
	}
	ret, _, _ := usrNetLocalGroupAddMembers.Call(
		uintptr(0),                          // servername
		uintptr(unsafe.Pointer(gPointer)),   // group name
		uintptr(uint32(3)),                  // level
		uintptr(unsafe.Pointer(&uArray[0])), // user array.
		uintptr(uint32(len(uArray))),
	)
	if ret != NET_API_STATUS_NERR_Success {
		return false, fmt.Errorf("Unable to process. %d", ret)
	}
	return true, nil
}

func removeGroupMembership(username, groupname string) (bool, error) {
	hn, _ := os.Hostname()
	uPointer, err := syscall.UTF16PtrFromString(hn + `\` + username)
	if err != nil {
		return false, fmt.Errorf("Unable to encode username to UTF16")
	}
	gPointer, err := syscall.UTF16PtrFromString(groupname)
	if err != nil {
		return false, fmt.Errorf("Unable to encode group name to UTF16")
	}
	var uArray = make([]LOCALGROUP_MEMBERS_INFO_3, 1)
	uArray[0] = LOCALGROUP_MEMBERS_INFO_3{
		Lgrmi3_domainandname: uPointer,
	}
	ret, _, _ := usrNetLocalGroupDelMembers.Call(
		uintptr(0),                          // servername
		uintptr(unsafe.Pointer(gPointer)),   // group name
		uintptr(uint32(3)),                  // level
		uintptr(unsafe.Pointer(&uArray[0])), // user array.
		uintptr(uint32(len(uArray))),
	)
	if ret != NET_API_STATUS_NERR_Success {
		return false, fmt.Errorf("Unable to process. %d", ret)
	}
	return true, nil
}

func enumerateGroupMember(groupname string) ([]string, error) {
	gPointer, errP := syscall.UTF16PtrFromString(groupname)
	if errP != nil {
		return nil, fmt.Errorf("Unable to encode groupName to UTF16")
	}

	var mockOut *uint16
	var entryRead uint32
	var totalEntry uint32
	var handle uint32
	// first get entry nums
	ret, _, _ := usrNetLocalGroupGetMembers.Call(
		uintptr(0),
		uintptr(unsafe.Pointer(gPointer)),
		uintptr(uint32(1)),
		uintptr(unsafe.Pointer(&mockOut)),
		uintptr(uint32(8192*32)),
		uintptr(unsafe.Pointer(&entryRead)),
		uintptr(unsafe.Pointer(&totalEntry)),
		uintptr(unsafe.Pointer(&handle)),
	)

	if ret != NET_API_STATUS_NERR_Success {
		return nil, fmt.Errorf("Enum User from group failed! code: (0x%d)", int(ret))
	}

	enumUserData := make([]LOCALGROUP_MEMBERS_INFO_1, int(totalEntry))
	ret2, _, _ := usrNetLocalGroupGetMembers.Call(
		uintptr(0),
		uintptr(unsafe.Pointer(gPointer)),
		uintptr(uint32(1)),
		uintptr(unsafe.Pointer(&enumUserData)),
		uintptr(uint32(8192*32)),
		uintptr(unsafe.Pointer(&entryRead)),
		uintptr(unsafe.Pointer(&totalEntry)),
		uintptr(unsafe.Pointer(&handle)),
	)

	if ret2 != NET_API_STATUS_NERR_Success {
		return nil, fmt.Errorf("Enum User from group failed! code: (0x%d)", int(ret2))
	}

	finalUsers := make([]string, int(totalEntry))
	for k, v := range enumUserData {
		finalUsers[k] = utf16toString(v.lgrmi1_name)
	}

	return finalUsers, nil
}

func userUpdateFullname(username string, fullname string) (bool, error) {
	var errParam uint32
	uPointer, err := syscall.UTF16PtrFromString(username)
	if err != nil {
		return false, fmt.Errorf("Unable to encode username to UTF16")
	}
	fPointer, err := syscall.UTF16PtrFromString(fullname)
	if err != nil {
		return false, fmt.Errorf("Unable to encode full name to UTF16")
	}
	ret, _, _ := usrNetUserSetInfo.Call(
		uintptr(0),                        // servername
		uintptr(unsafe.Pointer(uPointer)), // username
		uintptr(uint32(1011)),             // level
		uintptr(unsafe.Pointer(&USER_INFO_1011{Usri1011_full_name: fPointer})),
		uintptr(unsafe.Pointer(&errParam)),
	)
	if ret != NET_API_STATUS_NERR_Success {
		return false, fmt.Errorf("Unable to process. %d", ret)
	}
	return true, nil
}

func userDisabled(username string, disable bool) (bool, error) {
	if disable {
		return userAddFlags(username, USER_UF_ACCOUNTDISABLE)
	}
	return userDelFlags(username, USER_UF_ACCOUNTDISABLE)
}

func userPasswordNoExpires(username string, noexpire bool) (bool, error) {
	if noexpire {
		return userAddFlags(username, USER_UF_DONT_EXPIRE_PASSWD)
	}
	return userDelFlags(username, USER_UF_DONT_EXPIRE_PASSWD)
}

func userDisablePasswordChange(username string, disabled bool) (bool, error) {
	if disabled {
		return userAddFlags(username, USER_UF_PASSWD_CANT_CHANGE)
	}
	return userDelFlags(username, USER_UF_PASSWD_CANT_CHANGE)
}

func userGetFlags(username string) (uint32, error) {
	var dataPointer uintptr
	uPointer, err := syscall.UTF16PtrFromString(username)
	if err != nil {
		return 0, fmt.Errorf("Unable to encode username to UTF16")
	}
	_, _, _ = usrNetUserGetInfo.Call(
		uintptr(0),                            // servername
		uintptr(unsafe.Pointer(uPointer)),     // username
		uintptr(uint32(1)),                    // level, request USER_INFO_1
		uintptr(unsafe.Pointer(&dataPointer)), // Pointer to struct.
	)
	defer usrNetApiBufferFree.Call(uintptr(unsafe.Pointer(dataPointer)))

	if dataPointer == uintptr(0) {
		return 0, fmt.Errorf("Unable to get data structure")
	}

	var data = (*USER_INFO_1)(unsafe.Pointer(dataPointer))

	fmt.Printf("Existing user flags: %d\r\n", data.Usri1_flags)
	return data.Usri1_flags, nil
}

func userSetFlags(username string, flags uint32) (bool, error) {
	var errParam uint32
	uPointer, err := syscall.UTF16PtrFromString(username)
	if err != nil {
		return false, fmt.Errorf("Unable to encode username to UTF16")
	}
	ret, _, _ := usrNetUserSetInfo.Call(
		uintptr(0),                        // servername
		uintptr(unsafe.Pointer(uPointer)), // username
		uintptr(uint32(1008)),             // level
		uintptr(unsafe.Pointer(&USER_INFO_1008{Usri1008_flags: flags})),
		uintptr(unsafe.Pointer(&errParam)),
	)
	if ret != NET_API_STATUS_NERR_Success {
		return false, fmt.Errorf("Unable to process. %d", ret)
	}
	return true, nil
}

func userAddFlags(username string, flags uint32) (bool, error) {
	eFlags, err := userGetFlags(username)
	if err != nil {
		return false, fmt.Errorf("Error while getting existing flags, %s", err.Error())
	}
	eFlags |= flags // add supplied bits to mask.
	return userSetFlags(username, eFlags)
}

func userDelFlags(username string, flags uint32) (bool, error) {
	eFlags, err := userGetFlags(username)
	if err != nil {
		return false, fmt.Errorf("Error while getting existing flags, %s", err.Error())
	}
	eFlags &^= flags // clear bits we want to remove.
	return userSetFlags(username, eFlags)
}

func utf16toString(p *uint16) string {
	return syscall.UTF16ToString((*[4096]uint16)(unsafe.Pointer(p))[:])
}

// Groups API
func addGroup(groupname string) error {
	gPointer, err := syscall.UTF16PtrFromString(groupname)
	if err != nil {
		return fmt.Errorf("Unable to encode groupname to UTF16")
	}
	// group comment
	cPointer, err2 := syscall.UTF16PtrFromString("auto-generated by aloha-panel")
	if err2 != nil {
		return fmt.Errorf("Unable to encode group comment to UTF16")
	}

	groupStruct := LOCALGROUP_INFO_1{
		lgrpi1_name:    gPointer,
		lgrpi1_comment: cPointer,
	}
	ret, _, _ := groupNetLocalGroupAdd.Call(
		uintptr(0),
		uintptr(1),
		uintptr(unsafe.Pointer(&groupStruct)),
		uintptr(0))

	if ret != NET_API_STATUS_NERR_Success {
		return fmt.Errorf("Add Group '%s' failed! code: (0x%x)", groupname, int(ret))
	}

	return nil
}

func removeGroup(groupname string) error {
	gPointer, err := syscall.UTF16PtrFromString(groupname)
	if err != nil {
		return fmt.Errorf("Unable to encode groupname to UTF16")
	}

	ret, _, _ := groupNetLocalGroupDel.Call(
		uintptr(0),
		uintptr(unsafe.Pointer(gPointer)),
	)

	if ret != NET_API_STATUS_NERR_Success {
		return fmt.Errorf("Remove Group '%s' failed! code: (0x%d)", groupname, int(ret))
	}

	return nil
}

func enumerateGroup() ([]string, error) {
	var mockOut *uint16
	var entryRead uint32
	var totalEntry uint32
	var handle uint32
	// first get entry nums
	ret, _, _ := groupNetLocalGroupEnum.Call(
		uintptr(0),
		uintptr(uint32(1)),
		uintptr(unsafe.Pointer(&mockOut)),
		uintptr(uint32(8192)),
		uintptr(unsafe.Pointer(&entryRead)),
		uintptr(unsafe.Pointer(&totalEntry)),
		uintptr(unsafe.Pointer(&handle)),
	)

	if ret != NET_API_STATUS_NERR_Success {
		return nil, fmt.Errorf("Enum Group failed! code: (0x%d)", int(ret))
	}

	enumGroupData := make([]LOCALGROUP_INFO_1, int(totalEntry))
	ret2, _, _ := groupNetLocalGroupEnum.Call(
		uintptr(0),
		uintptr(uint32(1)),
		uintptr(unsafe.Pointer(&enumGroupData)),
		uintptr(uint32(8192)),
		uintptr(unsafe.Pointer(&entryRead)),
		uintptr(unsafe.Pointer(&totalEntry)),
		uintptr(unsafe.Pointer(&handle)),
	)

	if ret2 != NET_API_STATUS_NERR_Success {
		return nil, fmt.Errorf("Enum Group failed! code: (0x%d)", int(ret2))
	}

	finalGroups := make([]string, int(totalEntry))
	for k, v := range enumGroupData {
		finalGroups[k] = utf16toString(v.lgrpi1_name)
	}

	return finalGroups, nil
}

// Windows Local Security Authority (LSA) Management
// APIs:
// findSid(name string) (SID, error)
// lsaAddAccountRights(username string, rights []string) error
// lsaRemoveAccountRights(username string, rights []string, allRights bool) error
// lsaOpenPolicy() (LSA_HANDLE, error)
// lsaClose(handle LSA_HANDLE) error
// initLsaUnicodeString(lsaName string) (LSA_UNICODE_STRING, error)
//

func findSid(name string) (SID, error) {
	uPointer, err := syscall.UTF16PtrFromString(name)
	if err != nil {
		return nil, err
	}

	var sidBufferSize uint16
	var cch uint16

	sidBufferSize = 0
	cch = 0
	var sidType uint16
	// first get buffer size
	advLookupAccountName.Call(
		uintptr(0),
		uintptr(unsafe.Pointer(uPointer)),
		uintptr(0),
		uintptr(unsafe.Pointer(&sidBufferSize)),
		uintptr(0),
		uintptr(unsafe.Pointer(&cch)),
		uintptr(unsafe.Pointer(&sidType)),
	)

	// TODO: add error handling when sid not found
	// then get sid data
	var sid = make([]byte, sidBufferSize)
	// reserved
	var ref = make([]byte, cch)
	ret2, _, err3 := advLookupAccountName.Call(
		uintptr(0),
		uintptr(unsafe.Pointer(uPointer)),
		uintptr(unsafe.Pointer(&sid[0])),
		uintptr(unsafe.Pointer(&sidBufferSize)),
		uintptr(unsafe.Pointer(&ref[0])),
		uintptr(unsafe.Pointer(&cch)),
		uintptr(unsafe.Pointer(&sidType)),
	)

	if ret2 == 0 {
		return nil, err3
	}

	return sid, nil
}

func lsaAddAccountRights(username string, rights []string) error {
	handle, errOpen := lsaOpenPolicy()
	if errOpen != nil {
		return errOpen
	}
	defer lsaClose(handle)
	sid, errSid := findSid(username)
	if errSid != nil {
		return errSid
	}

	rightsLen := len(rights)
	userRights := make([]LSA_UNICODE_STRING, rightsLen)
	for k, v := range rights {
		val, e := initLsaUnicodeString(v)
		if e != nil {
			return e
		}
		userRights[k] = val
	}

	// call
	ret, _, _ := advLsaAddAccountRights.Call(
		uintptr(handle),
		uintptr(unsafe.Pointer(&sid[0])),
		uintptr(unsafe.Pointer(&userRights[0])),
		uintptr(uint16(rightsLen)),
	)

	if ret != STATUS_SUCCESS {
		return fmt.Errorf("AddAccountRights error! Code: (0x%x)", int(ret))
	}

	return nil
}

func lsaRemoveAccountRights(username string, rights []string, allRights bool) error {
	handle, errOpen := lsaOpenPolicy()
	if errOpen != nil {
		return errOpen
	}
	defer lsaClose(handle)

	sid, errSid := findSid(username)
	if errSid != nil {
		return errSid
	}

	userRights := make([]LSA_UNICODE_STRING, len(rights))
	for k, v := range rights {
		val, e := initLsaUnicodeString(v)
		if e != nil {
			return e
		}
		userRights[k] = val
	}

	allRightsNum := 0
	if allRights == true {
		allRightsNum = 1
	}
	// call
	ret, _, _ := advLsaRemoveAccountRights.Call(
		uintptr(handle),
		uintptr(unsafe.Pointer(&sid[0])),
		uintptr(allRightsNum),
		uintptr(unsafe.Pointer(&userRights[0])),
		uintptr(len(rights)),
	)

	if ret != STATUS_SUCCESS {
		return fmt.Errorf("AddAccountRights error! Code: (0x%x)", int(ret))
	}

	return nil
}

func lsaEnumerateAccountRights(username string) ([]string, error) {
	handle, errOpen := lsaOpenPolicy()
	if errOpen != nil {
		return nil, errOpen
	}
	defer lsaClose(handle)

	sid, errSid := findSid(username)
	if errSid != nil {
		return nil, errSid
	}

	var mockOut *uint16
	var countItems uint64
	// only get countItems
	ret, _, _ := advLsaEnumerateAccountRights.Call(
		uintptr(handle),
		uintptr(unsafe.Pointer(&sid[0])),
		uintptr(unsafe.Pointer(&mockOut)),
		uintptr(unsafe.Pointer(&countItems)))

	if ret != STATUS_SUCCESS {
		return nil, fmt.Errorf("Enum Account Rights error! Code: (0x%x)", int(ret))
	}
	// if there's no such
	if countItems == 0 {
		return []string{}, nil
	}
	// generate actual data to receive rights string
	actualLsaRights := make([]LSA_UNICODE_STRING, int(countItems))

	ret2, _, _ := advLsaEnumerateAccountRights.Call(
		uintptr(handle),
		uintptr(unsafe.Pointer(&sid[0])),
		uintptr(unsafe.Pointer(&actualLsaRights)),
		uintptr(unsafe.Pointer(&countItems)))

	if ret2 != STATUS_SUCCESS {
		return nil, fmt.Errorf("Enum Account Rights error! Code: (0x%x)", int(ret))
	}

	finalStr := make([]string, int(countItems))
	for k, v := range actualLsaRights {
		finalStr[k] = utf16toString(v.Buffer)
	}

	return finalStr, nil
}

func lsaOpenPolicy() (LSA_HANDLE, error) {
	objAttrs := LSA_OBJECT_ATTRIBUTES{}

	var handle LSA_HANDLE
	ret, _, _ := advLsaOpenPolicy.Call(
		uintptr(0),
		uintptr(unsafe.Pointer(&objAttrs)),
		POLICY_ALL_ACCESS,
		uintptr(unsafe.Pointer(&handle)),
	)

	if ret != STATUS_SUCCESS {
		return handle, fmt.Errorf("Open LSA Policy error! Code: (%d)", int(ret))
	}

	return handle, nil
}

func lsaClose(handle LSA_HANDLE) error {
	ret, _, _ := advLsaClose.Call(uintptr(handle))

	if ret != STATUS_SUCCESS {
		return fmt.Errorf("Close Lsa Object Error (code: %d)", int(ret))
	}

	return nil
}

// Access Token Privilege API
func lookupPrivilegeValue(privilege string) (LUID, error) {
	uPointer, err := syscall.UTF16PtrFromString(privilege)
	if err != nil {
		return LUID{}, err
	}

	luid := LUID{}

	ret, _, errCall := advLookupPrivilegeValue.Call(
		uintptr(0),
		uintptr(unsafe.Pointer(uPointer)),
		uintptr(unsafe.Pointer(&luid)))

	if ret == 0 {
		return LUID{}, errCall
	}

	return luid, nil
}

func setTokenPrivilege(tokenHandle uintptr, privilege string, enable bool) error {
	// 1. Get LUID first
	luid, errL := lookupPrivilegeValue(privilege)
	if errL != nil {
		return errL
	}

	lattr := uint32(SE_PRIVILEGE_REMOVED)
	if enable == true {
		lattr = uint32(SE_PRIVILEGE_ENABLED)
	}
	// 2. construct token privledge
	luidAttr := LUID_AND_ATTRIBUTES{
		Luid:       luid,
		Attributes: lattr,
	}

	tokenPriv := TOKEN_PRIVILEGES{
		PrivilegeCount: uint32(1),
		Privileges:     luidAttr,
	}

	// 3. call function
	ret, _, errCall := advAdjustTokenPrivileges.Call(
		tokenHandle,
		uintptr(0),
		uintptr(unsafe.Pointer(&tokenPriv)),
		uintptr(unsafe.Sizeof(tokenPriv)),
		uintptr(0),
		uintptr(0))

	if ret == 0 {
		return errCall
	}

	return nil
}

// duplicate  to get primary access token
func getPrimaryToken(oldToken uintptr) (uintptr, error) {

	var newToken uintptr

	ret, _, errCall := advDuplicateTokenEx.Call(
		oldToken,
		uintptr(uint32(TOKEN_ALL_ACCESS|GENERIC_ALL_ACCESS)),
		uintptr(0),
		uintptr(SecurityImpersonation),
		uintptr(TokenPrimary),
		uintptr(unsafe.Pointer(&newToken)))

	if ret == 0 {
		return uintptr(0), errCall
	}

	return newToken, nil
}

func enterUserContext(userToken uintptr) error {
	ret, _, errCall := advImpersonateLoggedOnUser.Call(userToken)

	if ret == 0 {
		return errCall
	}
	return nil
}

func exitUserContext() error {
	ret, _, errCall := advRevertToSelf.Call()

	if ret == 0 {
		return errCall
	}
	return nil
}

// helper functions
func initLsaUnicodeString(lsaName string) (LSA_UNICODE_STRING, error) {

	buf, _ := syscall.UTF16FromString(lsaName)
	bufLen := uint16(len(buf))
	if bufLen > 0x7ffe {
		return LSA_UNICODE_STRING{}, errors.New("LsaName length exceeds limit")
	}

	return LSA_UNICODE_STRING{
		Buffer:        &buf[0],
		Length:        (bufLen - 1) * 2,
		MaximumLength: bufLen * 2,
	}, nil
}
