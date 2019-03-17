package account

/*
func signJWT(payload map[string]interface{}, config *infra.Config) (jwt string, err error) {
	claims := jwtLib.MapClaims{}
	var expTime int64
	for key, val := range payload {
		claims[key] = val
	}

	claims["iss"] = config.Issuer
	expTime = time.Now().Add(config.ExpireIn).Unix()
	claims["exp"] = expTime

	token := jwtLib.NewWithClaims(jwtLib.SigningMethodHS256, claims)
	jwt, err = token.SignedString([]byte(config.Secret))
	return
}
*/
