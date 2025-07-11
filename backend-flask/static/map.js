var allMarkerData = [];  // 모든 마커 데이터를 저장할 배열

// 메시지 수신 처리
window.addEventListener("message", function (event) {
    const allowedOrigins = [
        "https://news.mojuk.kr",
        "http://127.0.0.1:8081",  // 로컬 개발 환경 주소
        "http://localhost:8081"
    ];

    if (!allowedOrigins.includes(event.origin)) {
        console.warn("Unauthorized origin: ", event.origin);
        return;
    }

    const receivedData = event.data;
    // console.log("Received Data:", receivedData);

    // 'action'이 'add'인 경우에는 마커 추가, 'remove'인 경우에는 마커 제거
    if (receivedData.action === "add") {
        // 받은 데이터 처리
        const newData = receivedData.data;

        // 마커 초기화
        allMarkerData = [];

        newData.forEach(item => {
            const uniqueKey = `${item.schoolNames}-${item.dataCount}`;

            // 기존에 있는 데이터를 중복없이 누적
            const existingItem = allMarkerData.find(existingItem => `${existingItem.schoolNames}-${existingItem.dataCount}` === uniqueKey);
            if (!existingItem) {
                //allMarkerData.push(item);  // 중복되지 않으면 추가
                // 전형별로 데이터 구조 변환
                const typeGroups = {}; // 전형별로 데이터를 분리
                if (item.type && item.dataCount) {
                    typeGroups[item.type] = item.dataCount;
                }

                // 변환된 데이터를 allMarkerData에 추가
                allMarkerData.push({
                    schoolNames: item.schoolNames,
                    typeGroups: item.typeGroups,
                    dataCount: item.dataCount
                });
            }
        });
    } else if (receivedData.action === "remove") {
        // 마커가 제거될 때 해당 데이터를 allMarkerData에서 제거
        const removeData = receivedData.data;

        // 제거할 데이터가 있으면 배열에서 삭제
        removeData.forEach(item => {
            const index = allMarkerData.findIndex(existingItem => `${existingItem.schoolNames}-${existingItem.dataCount}` === `${item.schoolNames}-${item.dataCount}`);
            if (index !== -1) {
                allMarkerData.splice(index, 1);  // 데이터 삭제
            }
        });
    }

    //console.log("Updated Marker Data:", allMarkerData);
    updateTable(allMarkerData);  // 테이블 업데이트
});

// DOMContentLoaded 이벤트 리스너
document.addEventListener("DOMContentLoaded", function () {
    const allCheckbox = document.getElementById("check_all");
    const otherCheckboxes = document.querySelectorAll('.form-check-input:not(#check_all)');

    // 전체 체크박스를 변경할 때
    allCheckbox.addEventListener("change", () => {
        otherCheckboxes.forEach(cb => cb.checked = allCheckbox.checked);
        updateTable(allMarkerData);
    });

    // 나머지 체크박스 변경 시 전체 체크 상태 반영
    otherCheckboxes.forEach(cb => {
        cb.addEventListener("change", () => {
            const allChecked = Array.from(otherCheckboxes).every(cb => cb.checked);
            allCheckbox.checked = allChecked;
            updateTable(allMarkerData);
        });
    });

    // 초기에 테이블 렌더링
    updateTable(allMarkerData);
});

function updateTable(data) {
    const tableBody = document.querySelector(".map-table tbody");
    tableBody.innerHTML = ""; // 기존 테이블 내용 초기화

    // 체크박스
    const selectedTypes = Array.from(document.querySelectorAll('.form-check-input:checked'))
        .map(checkbox => checkbox.value);

    // 데이터를 '지원자 수(dataCount)'를 기준으로 내림차순 정렬
    const sortedData = data.sort((a, b) => b.dataCount - a.dataCount);

    // 테이블에 데이터 추가
    sortedData.forEach((item, index) => {
        const schoolName = item.schoolNames;
        const typeGroups = item.typeGroups;

        for (const type in typeGroups) {
            // 선택된 전형만 테이블에 표시
            if (selectedTypes.includes(type)) {
                const row = document.createElement("tr");

                // No
                const noCell = document.createElement("td");
                noCell.textContent = index + 1;
                row.appendChild(noCell);

                // 모집전형
                const typeCell = document.createElement("td");
                typeCell.textContent = type;
                row.appendChild(typeCell);

                // 고교명
                const schoolNamesCell = document.createElement("td");
                schoolNamesCell.textContent = schoolName;
                row.appendChild(schoolNamesCell);

                // 지원자 수
                const dataCountCell = document.createElement("td");
                dataCountCell.textContent = typeGroups[type];
                row.appendChild(dataCountCell);

                tableBody.appendChild(row);
            }
        }
    });
}
