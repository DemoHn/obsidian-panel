// +build windows

package account

/*
import (
	"math/rand"
	"strings"
	"time"

	. "github.com/franela/goblin"
)

// generate rand string: copied from https://stackoverflow.com/questions/22892120/how-to-generate-a-random-string-of-a-fixed-length-in-golang
var letters = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

func genRandName(count int, prefix bool) string {
	rand.Seed(time.Now().UTC().UnixNano())
	b := make([]rune, count)
	for i := range b {
		b[i] = letters[rand.Intn(len(letters))]
	}

	if prefix == true {
		return "TEST-" + string(b)
	}
	return string(b)
}

func stringContains(dest string, src []string) bool {
	result := false
	for _, v := range src {
		if strings.Compare(dest, v) == 0 {
			result = true
			break
		}
	}
	return result
}


func Test(t *testing.T) {
	g := Goblin(t)

	g.Describe("Add & Remove & Enum Groups", func() {
		groupName := genRandName(8, true)
		g.It("should add groups", func() {
			eGroup := addGroup(groupName)
			g.Assert(eGroup).Equal(nil)

			groups, eG := enumerateGroup()
			g.Assert(eG).Equal(nil)
			g.Assert(stringContains(groupName, groups)).Equal(true)
		})

		g.It("should remove groups", func() {
			eGroup := removeGroup(groupName)
			g.Assert(eGroup).Equal(nil)

			groups, eG := enumerateGroup()
			g.Assert(eG).Equal(nil)
			g.Assert(stringContains(groupName, groups)).Equal(false)
		})
	})

	g.Describe("Add & Remove User", func() {
		expGroup := genRandName(3, true)
		expUser := genRandName(5, false)

		expPass := "password"
		g.Before(func() {
			addGroup(expGroup)
		})

		g.It("should add users", func() {
			isSuccess, eUser := userAdd(expUser, expUser, expPass, expGroup)
			g.Assert(eUser).Equal(nil)
			g.Assert(isSuccess).Equal(true)

			users, eU := enumerateGroupMember(expGroup)
			g.Assert(eU).Equal(nil)
			g.Assert(stringContains(expUser, users)).Equal(true)
		})

		g.It("should remove users", func() {
			isSuccess, eUser := userDelete(expUser)
			g.Assert(eUser).Equal(nil)
			g.Assert(isSuccess).Equal(true)

			users, eU := enumerateGroupMember(expGroup)
			g.Assert(eU).Equal(nil)
			g.Assert(stringContains(expUser, users)).Equal(false)
		})

		g.After(func() {
			removeGroup(expGroup)
		})
	})

	g.Describe("Add & Remove LSA", func() {
		expGroup := genRandName(8, false)
		expUser := genRandName(10, false)

		expPass := "password"

		rights := []string{
			"SeBatchLogonRight",
			"SeNetworkLogonRight",
		}

		removeRights1 := []string{
			"SeBatchLogonRight",
		}

		g.Before(func() {
			addGroup(expGroup)
			userAdd(expUser, expUser, expPass, expGroup)
		})

		g.It("should add privs", func() {
			e := lsaAddAccountRights(expUser, rights)
			g.Assert(e).Equal(nil)

			existingRights, err := lsaEnumerateAccountRights(expUser)
			g.Assert(err).Equal(nil)

			g.Assert(stringContains(rights[0], existingRights)).Equal(true)
			g.Assert(stringContains(rights[1], existingRights)).Equal(true)
		})

		g.It("should remove privs#1", func() {
			e := lsaRemoveAccountRights(expUser, removeRights1, false)
			g.Assert(e).Equal(nil)

			existingRights, err := lsaEnumerateAccountRights(expUser)
			g.Assert(err).Equal(nil)

			g.Assert(stringContains(rights[0], existingRights)).Equal(false)
			g.Assert(stringContains(rights[1], existingRights)).Equal(true)
		})

		g.After(func() {
			userDelete(expUser)
			removeGroup(expGroup)
		})
	})
}
*/
