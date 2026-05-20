package main

import "fmt"

// Greeter greets people
type Greeter struct {
    Name string
}

func (g *Greeter) Greet() string {
    return fmt.Sprintf("Hello, %s!", g.Name)
}

func fetchData(url string) (map[string]interface{}, error) {
    return nil, nil
}

func main() {
    g := &Greeter{Name: "World"}
    fmt.Println(g.Greet())
}
