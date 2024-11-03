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



// 복사 버튼 생성
function copylinkbtn() {
    const container = document.getElementById("urlzone");
    let btn = document.createElement("button");
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


// 입력 키워드 전부 가져오기
function getAllItem() {
    const keywordAreas = document.querySelectorAll('.keyword-area');
    const inputValues = Array.from(keywordAreas)
                        .map(area => area.querySelector('input').value)
                        .filter(value => value !== "");

    //console.log(inputValues);
    return inputValues;
}





const chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

// URL을 정수 해시로 변환 후 Base62로 인코딩
function base62Encode(num) {
    let encoded = '';
    while (num > 0) {
        encoded = chars[num % 62] + encoded;
        num = Math.floor(num / 62);
    }
    return encoded;
}

// URL을 정수 해시로 변환 (간단한 해시 방법)
function hashURL(url) {
    let hash = 0;
    for (let i = 0; i < url.length; i++) {
        hash = (hash * 31 + url.charCodeAt(i)) % 1000000007;  // 해시 충돌 줄이기
    }
    return hash;
}
