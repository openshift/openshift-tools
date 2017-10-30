package xmldom

import "bytes"

type Node struct {
	Document   *Document
	Parent     *Node
	Name       string
	Attributes []*Attribute
	Children   []*Node
	Text       string
}

type Attribute struct {
	Name  string
	Value string
}

func (n *Node) Root() *Node {
	return n.Document.Root
}

func (n *Node) GetAttribute(name string) *Attribute {
	for _, attr := range n.Attributes {
		if attr.Name == name {
			return attr
		}
	}
	return nil
}

func (n *Node) GetAttributeValue(name string) string {
	attr := n.GetAttribute(name)
	if attr != nil {
		return attr.Value
	}
	return ""
}

func (n *Node) SetAttributeValue(name string, value string) *Node {
	attr := n.GetAttribute(name)
	if attr != nil {
		attr.Value = value
	} else {
		n.Attributes = append(n.Attributes, &Attribute{name, value})
	}
	return n
}

func (n *Node) RemoveAttribute(name string) *Node {
	for i, attr := range n.Attributes {
		if attr.Name == name {
			n.Attributes = append(n.Attributes[:1], n.Attributes[i+1:]...)
			break
		}
	}
	return n
}

func (n *Node) GetChild(name string) *Node {
	for _, c := range n.Children {
		if c.Name == name {
			return c
		}
	}
	return nil
}

func (n *Node) GetChildren(name string) []*Node {
	var nodes []*Node
	for _, c := range n.Children {
		if c.Name == name {
			nodes = append(nodes, c)
		}
	}
	return nodes
}

func (n *Node) FirstChild() *Node {
	if len(n.Children) > 0 {
		return n.Children[0]
	}
	return nil
}

func (n *Node) LastChild() *Node {
	if l := len(n.Children); l > 0 {
		return n.Children[l-1]
	}
	return nil
}

func (n *Node) PrevSibling() *Node {
	if n.Parent != nil {
		for i, c := range n.Parent.Children {
			if c == n {
				if i >= 0 {
					return n.Parent.Children[i-1]
				}
				return nil
			}
		}
	}
	return nil
}

func (n *Node) NextSibling() *Node {
	if n.Parent != nil {
		for i, c := range n.Parent.Children {
			if c == n {
				if i+1 < len(n.Parent.Children) {
					return n.Parent.Children[i+1]
				}
				return nil
			}
		}
	}
	return nil
}

func (n *Node) CreateNode(name string) *Node {
	newNode := &Node{
		Name: name,
	}
	n.AppendChild(newNode)
	return newNode
}

func (n *Node) AppendChild(c *Node) *Node {
	c.Document = n.Document
	c.Parent = n
	n.Children = append(n.Children, c)
	return n
}

func (n *Node) RemoveChild(c *Node) *Node {
	for i, a := range n.Children {
		if a == c {
			n.Children = append(n.Children[:1], n.Children[i+1:]...)
			break
		}
	}
	return n
}

func (n *Node) FindByID(id string) *Node {
	if n.GetAttributeValue("id") == id {
		return n
	}

	for _, c := range n.Children {
		if x := c.FindByID(id); x != nil {
			return x
		}
	}

	return nil
}

func (n *Node) FindOneByName(name string) *Node {
	if n.Name == name {
		return n
	}

	for _, c := range n.Children {
		if x := c.FindOneByName(name); x != nil {
			return x
		}
	}

	return nil
}

func (n *Node) FindByName(name string) []*Node {
	var nodes []*Node

	if n.Name == name {
		nodes = append(nodes, n)
	}

	for _, c := range n.Children {
		nodes = append(nodes, c.FindByName(name)...)
	}

	return nodes
}

func (n *Node) Query(xpath string) []*Node {
	return xpathQuery(n, xpath)
}

func (n *Node) QueryOne(xpath string) *Node {
	return xpathQueryOne(n, xpath)
}

func (n *Node) QueryEach(xpath string, cb func(int, *Node)) {
	xpathQueryEach(n, xpath, cb)
}

func (n *Node) XML() string {
	buf := new(bytes.Buffer)
	printXML(buf, n, 0, "")
	return buf.String()
}

func (n *Node) XMLPretty() string {
	buf := new(bytes.Buffer)
	printXML(buf, n, 0, "  ")
	return buf.String()
}
