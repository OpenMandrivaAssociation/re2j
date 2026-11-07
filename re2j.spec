Name:		re2j
Version:	1.8
Release:	1
Summary:	Linear-time regular expressions for Java
Group:		Development/Java
License:	BSD-3-Clause
URL:		https://github.com/google/re2j
Source0:	https://github.com/google/re2j/archive/refs/tags/re2j-%{version}.tar.gz#/re2j-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name re2j --link %{name} --alias com.google.re2j:re2j

%description
RE2/J is a Java port of RE2. Matching runs in time linear in the size
of the input. 1.8 is the current release. The build targets Java 8 and
skips tests. The GWT super-sources are not compiled. The automatic
module name is com.google.re2j.

%prep
%autosetup -n re2j-re2j-%{version}
python - <<'PY'
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

super_dir = Path("java/com/google/re2j/super")
if not super_dir.is_dir():
    raise SystemExit("GWT super-sources missing")
shutil.rmtree(super_dir)
kept = [p for p in Path("java").rglob("*.java")]
if len(kept) != 19:
    raise SystemExit("unexpected java file count " + str(len(kept)))

NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def tag(name):
    return "{" + NS + "}" + name

def add(parent, name, text):
    node = ET.SubElement(parent, tag(name))
    node.text = text
    return node

root = ET.Element(tag("project"))
add(root, "modelVersion", "4.0.0")
add(root, "groupId", "com.google.re2j")
add(root, "artifactId", "re2j")
add(root, "version", "%{version}")
add(root, "name", "RE2/J")
props = ET.SubElement(root, tag("properties"))
add(props, "maven.compiler.release", "8")
build = ET.SubElement(root, tag("build"))
add(build, "sourceDirectory", "java")
ET.ElementTree(root).write("pom.xml", encoding="utf-8", xml_declaration=True)
text = Path("pom.xml").read_text(encoding="utf-8")
if "<sourceDirectory>java</sourceDirectory>" not in text:
    raise SystemExit("source directory missing")
if "<maven.compiler.release>8</maven.compiler.release>" not in text:
    raise SystemExit("compiler release missing")
PY

%build -a
cat > manifest-addition <<'EOF'
Automatic-Module-Name: com.google.re2j
EOF
jar ufm target/re2j-%{version}.jar manifest-addition
java --module-path target/re2j-%{version}.jar --describe-module com.google.re2j | grep -q '^com.google.re2j'

%files -f .mfiles
%doc LICENSE README.md
