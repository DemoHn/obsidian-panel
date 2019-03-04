package srpc

// RPC - RPC Type receiver (usually for testing)
type RPC int

// Echo - echo data
func (r *RPC) Echo(input string, output *string) error {
	*output = input
	return nil
}
