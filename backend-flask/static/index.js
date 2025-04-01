// ============================================
// 화면 로딩 후 기본 페이지 로드 및 뉴스데이터 비동기 요청
$(document).ready(function () {
    //ajax_get_data();
    ajax_get_data_from_file();
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


