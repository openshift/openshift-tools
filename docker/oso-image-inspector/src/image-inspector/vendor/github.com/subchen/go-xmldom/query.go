package xmldom

import (
	"github.com/antchfx/xpath"
)

// createXPathNavigator creates a new xpath.NodeNavigator for the specified xmldom.Node.
func createXPathNavigator(top *Node) xpath.NodeNavigator {
	return &xmlNodeNavigator{curr: top, attrIndex: -1}
}

// xpathQuery searches the Node that matches by the specified XPath expr.
func xpathQuery(top *Node, expr string) []*Node {
	t := xpath.Select(createXPathNavigator(top), expr)
	var nodes []*Node
	for t.MoveNext() {
		nodes = append(nodes, (t.Current().(*xmlNodeNavigator)).curr)
	}
	return nodes
}

// xpathQueryOne searches the Node that matches by the specified XPath expr,
// and returns first element of matched.
func xpathQueryOne(top *Node, expr string) *Node {
	t := xpath.Select(createXPathNavigator(top), expr)
	if t.MoveNext() {
		return (t.Current().(*xmlNodeNavigator)).curr
	}
	return nil
}

// xpathQueryEach searches the xmldom.Node and calls functions cb.
func xpathQueryEach(top *Node, expr string, cb func(int, *Node)) {
	t := xpath.Select(createXPathNavigator(top), expr)
	var i int
	for t.MoveNext() {
		cb(i, (t.Current().(*xmlNodeNavigator)).curr)
		i++
	}
}

type xmlNodeNavigator struct {
	curr      *Node
	attrIndex int
}

func (x *xmlNodeNavigator) NodeType() xpath.NodeType {
	if x.curr == x.curr.Root() {
		return xpath.RootNode
	}
	if x.attrIndex != -1 {
		return xpath.AttributeNode
	}
	return xpath.ElementNode
}

func (x *xmlNodeNavigator) LocalName() string {
	if x.attrIndex != -1 {
		return x.curr.Attributes[x.attrIndex].Name
	}
	return x.curr.Name
}

func (x *xmlNodeNavigator) Prefix() string {
	return ""
}

func (x *xmlNodeNavigator) Value() string {
	if x.attrIndex != -1 {
		return x.curr.Attributes[x.attrIndex].Value
	}
	return x.curr.Text
}

func (x *xmlNodeNavigator) Copy() xpath.NodeNavigator {
	n := *x
	return &n
}

func (x *xmlNodeNavigator) MoveToRoot() {
	x.curr = x.curr.Root()
}

func (x *xmlNodeNavigator) MoveToParent() bool {
	if node := x.curr.Parent; node != nil {
		x.curr = node
		return true
	}
	return false
}

func (x *xmlNodeNavigator) MoveToNextAttribute() bool {
	if x.attrIndex >= len(x.curr.Attributes)-1 {
		return false
	}
	x.attrIndex++
	return true
}

func (x *xmlNodeNavigator) MoveToChild() bool {
	if node := x.curr.FirstChild(); node != nil {
		x.curr = node
		return true
	}
	return false
}

func (x *xmlNodeNavigator) MoveToFirst() bool {
	if x.curr.Parent != nil {
		node := x.curr.Parent.FirstChild()
		if node != nil {
			x.curr = node
			return true
		}
	}
	return false
}

func (x *xmlNodeNavigator) MoveToPrevious() bool {
	node := x.curr.PrevSibling()
	if node != nil {
		x.curr = node
		return true
	}
	return false
}

func (x *xmlNodeNavigator) MoveToNext() bool {
	node := x.curr.NextSibling()
	if node != nil {
		x.curr = node
		return true
	}
	return false
}

func (x *xmlNodeNavigator) MoveTo(other xpath.NodeNavigator) bool {
	node, ok := other.(*xmlNodeNavigator)
	if !ok || node.curr.Root() != x.curr.Root() {
		return false
	}

	x.curr = node.curr
	x.attrIndex = node.attrIndex
	return true
}

func (x *xmlNodeNavigator) String() string {
	return x.Value()
}
