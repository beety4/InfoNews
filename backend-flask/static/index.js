// ============================================
// 화면 로딩 후 기본 페이지 로드 및 뉴스데이터 비동기 요청
$(document).ready(function () {
    //ajax_get_data();
    ajax_get_data_from_file();
});



// 입학지도 pwd 검증
// 라디오 버튼 체크 상태 변경 감지
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}


document.addEventListener("DOMContentLoaded", () => {
    const aboutRadio = document.getElementById("about");

    aboutRadio.addEventListener("change", async (event) => {
      if (aboutRadio.checked) {
        const isAuthenticated = getCookie("authenticated");
        if (isAuthenticated === "true") {
          // 이미 인증된 경우 - 허용
          return;
        }

        // 공백 검사
        const password = prompt("비밀번호를 입력하세요:");
        if (!password) {
          aboutRadio.checked = false;
          document.getElementById('contact').checked = true;
          return;
        }

        aboutRadio.checked = false;
        document.getElementById('contact').checked = true;
        const response = await fetch("/validatePwd", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ password }),
        });

        const result = await response.json();

        // 인증 처리 결과 분기
        if (result.success) {
          aboutRadio.checked = true;
        } else {
          aboutRadio.checked = false;
          document.getElementById('contact').checked = true;
          alert("비밀번호가 틀렸습니다.");
        }
      }
    });
});








// ============================================
// 사이트 처음로딩과 동시에 뉴스 데이터 비동기 요청
// 전체 선택
/*
    function selectAll() {
        document.querySelectorAll('.item-checkbox').forEach(checkbox => {
            checkbox.checked = true;
            toggleInput(checkbox);
        });
    }

    // 전체 해제
    function deselectAll() {
        document.querySelectorAll('.item-checkbox').forEach(checkbox => {
            checkbox.checked = false;
            toggleInput(checkbox);
        });
    }

    // 체크박스 선택 시 동적으로 입력 필드 추가
    function toggleInput(checkbox) {
        const inputContainer = document.getElementById('inputContainer');
        const existingInput = document.getElementById(`input-${checkbox.value}`);

        if (checkbox.checked) {
            if (!existingInput) {
                const newInput = document.createElement("input");
                newInput.type = "text";
                newInput.id = `input-${checkbox.value}`;
                newInput.placeholder = `${checkbox.value} 추가 입력`;
                newInput.style.display = "block";
                newInput.style.marginTop = "5px";
                inputContainer.appendChild(newInput);
            }
        } else {
            if (existingInput) {
                existingInput.remove();
            }
        }
    }
*/


