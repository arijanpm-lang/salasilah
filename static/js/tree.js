function buildTree(members) {
    const treeContainer = document.getElementById("tree");
    treeContainer.innerHTML = "";

    // Buat dict parent-child
    const memberMap = {};
    members.forEach(m => memberMap[m.id] = {...m, children: []});
    members.forEach(m => {
        if (m.parent_id) memberMap[m.parent_id].children.push(memberMap[m.id]);
    });

    const roots = members.filter(m => !m.parent_id).map(m => memberMap[m.id]);

    function createNode(member) {
        const li = document.createElement("li");
        const span = document.createElement("span");
        span.textContent = member.name;
        span.style.cursor = "pointer";
        span.style.backgroundColor = "#4CAF50";
        span.style.color = "white";
        span.style.padding = "5px 10px";
        span.style.borderRadius = "5px";

        // Klik node untuk paparan detail dan aksi
        span.addEventListener("click", () => {
            const action = prompt(
                `Ahli: ${member.name}\nTarikh Lahir: ${member.birth_date || '-'}\n\nPilih aksi:\n1. Edit Ahli\n2. Tambah Anak\n0. Batal`
            );
            if (action === "1") {
                window.location.href = `/edit_member/${member.id}`;
            } else if (action === "2") {
                window.location.href = `/add_member?parent_id=${member.id}`;
            }
        });

        li.appendChild(span);

        if (member.children.length > 0) {
            const ul = document.createElement("ul");
            member.children.forEach(child => ul.appendChild(createNode(child)));
            li.appendChild(ul);
        }
        return li;
    }

    const ul = document.createElement("ul");
    roots.forEach(root => ul.appendChild(createNode(root)));
    treeContainer.appendChild(ul);
}