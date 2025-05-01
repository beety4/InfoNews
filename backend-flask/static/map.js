var allMarkerData = [];  // 모든 마커 데이터를 저장할 배열

// 메시지 수신 처리
window.addEventListener("message", function (event) {
    if (event.origin !== "https://news.mojuk.kr") {
        console.warn("Unauthorized origin: ", event.origin);
        return;
    }

    const receivedData = event.data;
    console.log("Received Data:", receivedData);

    // 'action'이 'add'인 경우에는 마커 추가, 'remove'인 경우에는 마커 제거
    if (receivedData.action === "add") {
        // 받은 데이터 처리
        const newData = receivedData.data;

        newData.forEach(item => {
            const uniqueKey = `${item.schoolNames}-${item.dataCount}`;

            // 기존에 있는 데이터를 중복없이 누적
            const existingItem = allMarkerData.find(existingItem => `${existingItem.schoolNames}-${existingItem.dataCount}` === uniqueKey);
            if (!existingItem) {
                allMarkerData.push(item);  // 중복되지 않으면 추가
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

    console.log("Updated Marker Data:", allMarkerData);
    updateTable(allMarkerData);  // 테이블 업데이트
});

function updateTable(data) {
    const tableBody = document.querySelector(".map-table tbody");
    tableBody.innerHTML = ""; // 기존 테이블 내용 초기화

    // 데이터를 '지원자 수(dataCount)'를 기준으로 내림차순 정렬
    const sortedData = data.sort((a,b) => b.dataCount - a.dataCount);

    // 테이블에 데이터 추가
    sortedData.forEach((item, index) => {
        const row = document.createElement("tr");

        // No 컬럼
        const noCell = document.createElement("td");
        noCell.textContent = index + 1;
        row.appendChild(noCell);

        // 모집전형 컬럼
        const typeCell = document.createElement("td");
        typeCell.textContent = item.;
        row.appendChild(typeCell);

        // 고교명 컬럼
        const schoolNamesCell = document.createElement("td");
        schoolNamesCell.textContent = item.schoolNames;
        row.appendChild(schoolNamesCell);

        // 지원자 수 컬럼
        const dataCountCell = document.createElement("td");
        dataCountCell.textContent = item.dataCount;
        row.appendChild(dataCountCell);

        // 표에 행 추가
        tableBody.appendChild(row);
    });
}
