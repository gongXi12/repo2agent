from repo2agent.models import FileNode, Interface, ProjectMeta


def test_file_node_creation():
    node = FileNode(path="src/main.py", is_dir=False, children=None)
    assert node.path == "src/main.py"
    assert node.is_dir is False
    assert node.children is None


def test_file_node_directory():
    child = FileNode(path="src/main.py", is_dir=False, children=None)
    parent = FileNode(path="src", is_dir=True, children=[child])
    assert parent.is_dir is True
    assert len(parent.children) == 1


def test_interface_creation():
    iface = Interface(
        name="fetch_data",
        kind="function",
        file_path="src/api.py",
        signature="def fetch_data(url: str) -> dict",
        docstring="Fetch data from URL",
    )
    assert iface.name == "fetch_data"
    assert iface.kind == "function"
    assert iface.docstring == "Fetch data from URL"


def test_project_meta_defaults():
    meta = ProjectMeta(
        name="test-project",
        description="A test project",
        languages=["Python"],
        frameworks=[],
        dependencies={"prod": [], "dev": []},
        scripts={},
        structure=FileNode(path=".", is_dir=True, children=[]),
        readme_excerpt="",
        entry_points=[],
        interfaces=[],
        has_tests=False,
        has_docs=False,
        has_ci=False,
    )
    assert meta.name == "test-project"
    assert meta.languages == ["Python"]
    assert meta.has_tests is False
