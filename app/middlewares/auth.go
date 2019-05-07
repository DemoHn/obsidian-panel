package middlewares

import (
	"database/sql"
	"fmt"
	"strings"

	"github.com/DemoHn/obsidian-panel/util"

	"github.com/labstack/echo"

	"github.com/DemoHn/obsidian-panel/app/drivers/sqlite"
)

// Auth - new auth middleware
func Auth(db *sqlite.Driver, perms ...string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// get header
			var authHeader = c.Request().Header.Get("Authorization")
			// authorize
			if len(perms) > 0 {
				jwt, err := parseAuthHeader(authHeader)
				if err != nil {
					return err
				}

				token, err := authenticateJWT(db, jwt)
				if err != nil {
					return err
				}

				var tokPerm = token["permission"]
				// check if permission validates
				for _, p := range perms {
					if p == tokPerm {
						return next(c)
					}
				}

				return fmt.Errorf("invalid permission: %s", tokPerm)
			}
			return next(c)
		}
	}
}

// internal function
func authenticateJWT(db *sqlite.Driver, jwt string) (map[string]interface{}, error) {
	// parse JWT to get accountID first
	token, err := util.DecodeJWT(jwt)
	if err != nil {
		return nil, err
	}

	// find corresponded secret key
	accountID, ok := token["accountId"]
	if !ok {
		return nil, fmt.Errorf("invalid JWT: `accountId` not found")
	}

	var findStmt = "select public_key from user_secrets where account_id = ?"
	var publicKey []byte
	if err := db.QueryRow(findStmt, accountID).Scan(&publicKey); err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("no secret stored for accountID:%d", accountID)
		}
		return nil, err
	}

	// validate jwt
	return util.VerifyAndDecodeJWT(jwt, publicKey)
}

func parseAuthHeader(authHeader string) (string, error) {
	const Bearer = "Bearer "
	if strings.HasPrefix(authHeader, Bearer) {
		return authHeader[len(Bearer):], nil
	}

	return "", fmt.Errorf("invalid authorization header (should be 'Bearer' prefix)")
}
