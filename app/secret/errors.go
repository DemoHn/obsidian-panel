package secret

import (
	"fmt"

	"github.com/DemoHn/obsidian-panel/infra"
)

var secretErrors *infra.ErrorClass

func init() {
	secretErrors = infra.NewErrorClass(201)
}

// AccountNotFoundError - any operation on secrets should authenticate
// the existance of accountID
func AccountNotFoundError(accountID int) *infra.Error {
	return secretErrors.NewError("AccountNotFoundError", 1, 400, fmt.Sprintf("accountID(%d) not found", accountID), accountID)
}

// UserSecretNotFoundError - user secret not found error
// usually used for `updateUserPublicKey()`
func UserSecretNotFoundError(accountID int) *infra.Error {
	return secretErrors.NewError("UserSecretNotFoundError", 2, 400, fmt.Sprintf("user secret of accountID(%d) not found", accountID), accountID)
}
