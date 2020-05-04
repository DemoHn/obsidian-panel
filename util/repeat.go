package util

// Repeat -
func Repeat(tpl string, count int) []string {
	res := []string{}
	for i := 0; i < count; i++ {
		res = append(res, tpl)
	}
	return res
}
