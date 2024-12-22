// 검색 기간 년도 지정 스크립트
var today = new Date();
var year = today.getFullYear();
var byear = today.getFullYear() - 1;
var month = ('0' + (today.getMonth() + 1)).slice(-2);
var day = ('0' + today.getDate()).slice(-2);
var dateString1 = byear + '-' + month  + '-' + day;
var dateString2 = year + '-' + month  + '-' + day;
document.getElementById('startDate').value= dateString1;
document.getElementById('endDate').value= dateString2;


// url 공유로 들어왔을 경우
var url = window.location.href;
//console.log("url size : " + url.length);
if(url.length >= 30) {
    url = new URL(url)
    const urlParams = url.searchParams;
    var keyword = urlParams.get('keyword');
    var startDate = urlParams.get('startDate');
    var endDate = urlParams.get('endDate');
    var timeUnit = urlParams.get('timeUnit');
    var imgpath = urlParams.get('imgpath')

    keyword_list = JSON.parse(keyword)
    const container = document.getElementById("main-area");
    const existingInputs = container.querySelectorAll('.keyword-area input');

    keyword_list.forEach((value, index) => {
    if (index < existingInputs.length) {
        existingInputs[index].value = value;
    } else {
        let newTabIndex = existingInputs.length + index + 1;
        const html = `
            <div class="keyword-area">
                <input type="text" tabIndex="${newTabIndex}" value="${value}" placeholder="검색어 입력">
                <button onclick="remove(this)">삭제</button>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', html);
    }
});


    document.getElementById('startDate').value= startDate;
    document.getElementById('endDate').value= endDate;
    document.querySelector(`input[name="timeUnit"][value="${timeUnit}"]`).checked = true;
    document.getElementById("wc-img").src = "static/wc-img/" + imgpath;
    document.getElementById("chart-img").src = "static/chart-img/" + imgpath;
}


/*
// 복사 버튼 생성
function copylinkbtn() {
    const container = document.getElementById("urlzone");
    let btn = document.createElement("button");
    btn.setAttribute("class", "copybtn")
    btn.innerText = "현재 결과 링크 복사";
    container.appendChild(btn);

    btn.addEventListener("click", function() {
        let link_value = document.getElementById("link_value");

        window.navigator.clipboard.writeText(link_value.value).then(() => {
            alert("링크가 성공적으로 복사되었습니다!");
        });
    });
}


// 복사 링크 생성
function writecopylink(keyword, startDate, endDate, timeUnit, imgpath) {
    var now_link = document.getElementById("link_value");

    new_link = window.location.href +
               "?keyword=" + keyword +
               "&startDate=" + startDate +
               "&endDate=" + endDate +
               "&timeUnit=" + timeUnit +
               "&imgpath=" + imgpath;

    now_link.value = new_link;
    console.log()
}


// 검색어 추가 버튼 클릭 함수
document.getElementById("add").addEventListener("click", function() {
    const container = document.getElementById("main-area");

    // 현재 존재하는 모든 input 요소의 tabindex 속성 값을 가져오기
    const inputs = container.querySelectorAll('input[tabIndex]');
    const lastTabIndex = Math.max(...Array.from(inputs).map(input => Number(input.getAttribute('tabIndex'))));

    // 다음 tabindex 값을 설정
    const newTabIndex = lastTabIndex + 1;

    const html = `
        <div class="keyword-area">
            <input type="text" tabIndex="${newTabIndex}" placeholder="검색어 입력">
            <button onclick="remove(this)">삭제</button>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', html);
});


// 검색어 삭제 버튼 클릭 함수
function remove(button) {
    button.parentElement.remove();
}



// 검색 버튼 클릭 함수
document.getElementById("search").addEventListener("click", function() {
    let keywordList = getAllItem();
    let startDate = document.getElementById("startDate").value;
    let endDate = document.getElementById("endDate").value;
    let timeUnit = document.querySelector('input[name="timeUnit"]:checked').value;

    if(keywordList.length < 2) {
        alert("비교할 키워드 2개 이상을 입력해 주세요.");
        return;
    }

    $.ajax({
    	url:"/queryItem",
        type:"post",
        dataType:"text",
        data:{"keywordList" : JSON.stringify(keywordList),
              "startDate" : startDate,
              "endDate" : endDate,
              "timeUnit" : timeUnit
            },
        success: function(data){
			// console.log(data);
			if(data == 1 || data == "1") {
			    alert("외부 API 연동에 실패하였습니다.");
			    return;
			}

            // 현재 정보로 copy 링크 작성 및 버튼 생성
            writecopylink(JSON.stringify(keywordList), startDate, endDate, timeUnit, data);
            document.querySelectorAll('.copybtn').forEach(element => {
                element.remove();
            });

            copylinkbtn();

            // 이미지 띄우기
			document.getElementById("wc-img").src = "static/wc-img/" + data;
			document.getElementById("chart-img").src = "static/chart-img/" + data;
        },
        error: function(request, status, error) {
			alert("비동기 요청 중 오류가 발생했습니다.");
			console.log("code : " + request.status);
			console.log("message : " + request.responseText);
			console.log("error : " + error);
		}
	});

});

*/
// 입력 키워드 전부 가져오기
function getAllItem() {
    const keywordAreas = document.querySelectorAll('.keyword-area');
    const inputValues = Array.from(keywordAreas)
                        .map(area => area.querySelector('input').value)
                        .filter(value => value !== "");

    //console.log(inputValues);
    return inputValues;
}

















let downloadname = "";

// 검색 버튼 클릭 함수
document.getElementById("trend-search").addEventListener("click", function() {
    //let keywordList = getAllItem();
    let universityGroup = document.querySelector('input[name="universityGroup"]:checked').value;
    let startDate = document.getElementById("startDate").value;
    let endDate = document.getElementById("endDate").value;
    let timeUnit = document.querySelector('input[name="timeUnit"]:checked').value;

    // 결과 표 가리기
    document.getElementById("trend_result_table").innerText = "";
    document.getElementById("downloadxlsx").style.display = 'none';
    //document.getElementById("trend_info").style.display = 'none';

    $.ajax({
    	url:"/queryItem",
        type:"post",
        dataType:"text",
        // data:{"keywordList" : JSON.stringify(keywordList),
        data:{"universityGroup" : universityGroup,
              "startDate" : startDate,
              "endDate" : endDate,
              "timeUnit" : timeUnit
            },
        success: function(data){
			//console.log(data);
			if(data == 1 || data == "1") {
			    alert("외부 API 연동에 실패하였습니다.");
			    return;
			}

            showTrendResult(data);
        },
        error: function(request, status, error) {
			alert("비동기 요청 중 오류가 발생했습니다.");
			console.log("code : " + request.status);
			console.log("message : " + request.responseText);
			console.log("error : " + error);
		}
	});

});


function showTrendResult(data) {
    // 이미지 띄우기
    let jsondata = JSON.parse(data);
    let whereimg = Object.keys(jsondata)[0];
    let tableData = jsondata[whereimg];
	document.getElementById("wc-img").src = "static/wc-img/" + whereimg;
	document.getElementById("chart-img").src = "static/chart-img/" + whereimg;
	//document.getElementById("wc-img").src = "static/wc-img/20241221-175317.png";
	//document.getElementById("chart-img").src = "static/chart-img/20241221-175317.png";

	downloadname = "static/xlsx/" + whereimg.split(".")[0] + ".xlsx";

	// HTML 테이블 생성
    let html = `<table class="custom-table trend-table">
                <thead>
                <tr>
                <th>대학명</th>`;

    // 헤더 생성
    let columns = Object.keys(tableData[0]).filter(col => col !== "대학명");
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += `    </tr>
                </thead>
                <tbody>`;

    // 데이터 행 생성
    tableData.forEach(row => {
        // '인하공전'인 경우에는 'highlight-row' 클래스를 추가
        let rowClass = row.대학명 === "인하공전" ? "highlight-row" : "";
        html += `<tr class="${rowClass}">
                    <td>${row.대학명}</td>`;
        columns.forEach(col => {
            html += `<td>${row[col] !== undefined ? row[col] : '-'}</td>`;
        });
        html += `</tr>`;
    });

    html += `</tbody>
             </table>`;

    // 테이블 추가
    document.getElementById("trend_result_table").innerHTML = html;
    document.getElementById("downloadxlsx").style.display = 'block';
    //document.getElementById("trend_info").style.display = 'block';
}



document.getElementById("downloadxlsx").addEventListener("click", function() {
    // 가상의 앵커 태그 생성
    //console.log(downloadname);
    const a = document.createElement("a");
    a.href = downloadname;
    a.download = downloadname.split("/")[2];  // 다운로드될 파일 이름 설정
    a.click();  // 다운로드 실행
});
