// static/js/app.js
document.addEventListener("DOMContentLoaded", () => {
  // 1) Navbar active 표시 (data-nav 가진 a 태그)
  const links = document.querySelectorAll("a[data-nav]");
  const path = window.location.pathname;

  links.forEach(a => {
    const href = a.getAttribute("href") || "";
    // 정확히 같거나, 하위 경로일 때 active
    if (href !== "/" && (path === href || path.startsWith(href + "/"))) {
      a.classList.add("active");
      // dropdown 안에 있으면 부모도 active 느낌 주기
      const dropdown = a.closest(".dropdown");
      if (dropdown) dropdown.querySelector(".dropdown-toggle")?.classList.add("active");
    }
  });

  // 2) 프로필 이미지 미리보기 (input[type=file][data-preview-target="#id"])
  document.querySelectorAll('input[type="file"][data-preview-target]').forEach(input => {
    input.addEventListener("change", () => {
      const targetSel = input.getAttribute("data-preview-target");
      const img = document.querySelector(targetSel);
      if (!img) return;

      const file = input.files?.[0];
      if (!file) { img.style.display = "none"; return; }

      if (!file.type.startsWith("image/")) {
        alert("이미지 파일만 업로드 가능합니다.");
        input.value = "";
        img.style.display = "none";
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        img.src = reader.result;
        img.style.display = "block";
      };
      reader.readAsDataURL(file);
    });
  });

  // 3) 전화번호 간단 포맷 (data-phone)
  document.querySelectorAll('input[data-phone]').forEach(input => {
    input.addEventListener("input", () => {
      let v = input.value.replace(/[^\d]/g, "");
      // 010xxxxxxxx 기준 단순 포맷
      if (v.length >= 3 && v.length <= 7) v = v.replace(/(\d{3})(\d+)/, "$1-$2");
      else if (v.length >= 8) v = v.replace(/(\d{3})(\d{4})(\d+)/, "$1-$2-$3");
      input.value = v;
    });
  });

  // 4) 주민번호 간단 포맷 (data-rrn) 000000-0000000
  document.querySelectorAll('input[data-rrn]').forEach(input => {
    input.addEventListener("input", () => {
      let v = input.value.replace(/[^\d]/g, "");
      if (v.length > 6) v = v.slice(0, 6) + "-" + v.slice(6, 13);
      input.value = v;
    });
  });
});
