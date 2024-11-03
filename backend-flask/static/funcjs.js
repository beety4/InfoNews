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
			console.log(data);
			if(data == 1 || data == "1") {
			    alert("외부 API 연동에 실패하였습니다.");
			    return;
			}

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


// 입력 키워드 전부 가져오기
function getAllItem() {
    const keywordAreas = document.querySelectorAll('.keyword-area');
    const inputValues = Array.from(keywordAreas)
                        .map(area => area.querySelector('input').value)
                        .filter(value => value !== "");

    //console.log(inputValues);
    return inputValues;
}

