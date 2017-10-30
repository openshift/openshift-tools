package util

func StrOrDefault(s string, d string) string {
	if len(s) == 0 { // s || d
		return d
	}
	return s
}

func Min(x, y int) int {
	if x < y {
		return x
	}
	return y
}

func StringInList(s string, l []string) bool {
	for _, opt := range l {
		if s == opt {
			return true
		}
	}
	return false
}
