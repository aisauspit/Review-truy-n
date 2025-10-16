async function postJSON(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(data)
  });
  return res.json();
}

document.getElementById("createBtn").addEventListener("click", async () => {
  const title = document.getElementById("title").value || "Review Tiên giới";
  const voice = document.getElementById("voice").value || "vi";
  const sectionsRaw = document.getElementById("sections").value.trim();
  if (!sectionsRaw) { alert("Vui lòng nhập sections."); return; }
  const lines = sectionsRaw.split("\n").map(l=>l.trim()).filter(Boolean);
  const sections = lines.map(l => {
    const parts = l.split("|");
    return { heading: parts[0] || "", text: parts[1] || parts[0] || "" };
  });

  document.getElementById("log").textContent = "Đang gửi yêu cầu tới server (vui lòng chờ trong lúc tạo audio + video)...";
  try {
    const resp = await postJSON("/create", { title, sections, voice });
    if (resp.ok) {
      const link = `/download/${resp.file}`;
      document.getElementById("downloadLink").href = link;
      document.getElementById("downloadLink").textContent = "Tải video về";
      document.getElementById("result").classList.remove("hidden");
      document.getElementById("log").textContent = "Video đã sẵn sàng — bấm 'Tải video về'.";
    } else {
      document.getElementById("log").textContent = "Lỗi: " + (resp.error || "Không xác định");
    }
  } catch (e) {
    document.getElementById("log").textContent = "Lỗi kết nối: " + e.message;
  }
});
