function ajax_get_data() {
    // count view
    count_value(9);

    $.ajax({
    	url:"/newsItem",
        type:"post",
        dataType:"json",
        data:{"None" : "None"},
        success: function(data){
			console.log(data);
			if(data == 1 || data == "1") {
			    alert("뉴스 정보를 불러오는데 실패하였습니다.");
			    return;
			}

            // 새로고침 버튼
            document.getElementById("refresh_news").style.display = 'inline-block';

            // 체크박스 표시  및 함수 정의
            document.getElementById("news-checkbox").style.display = 'block';

            // 가져온 json 데이터 파싱 후 forEach문으로 table 출력
            write_news_data(data);
        },
        error: function(request, status, error) {
			alert("비동기 요청 중 오류가 발생했습니다.");
			console.log("code : " + request.status);
			console.log("message : " + request.responseText);
			console.log("error : " + error);
		}
	});
}


function ajax_get_data_from_file() {
    $.ajax({
    	url:"/newsItemfromFile",
        type:"post",
        dataType:"json",
        data:{"None" : "None"},
        success: function(data){
			//console.log(data);
			if(data == 1 || data == "1") {
			    alert("뉴스 정보를 불러오는데 실패하였습니다.");
			    return;
			}

			// 크롤링 데이터 시간 확인
            let jsonData = JSON.parse(data);
            //console.log(jsonData[1]);
            document.getElementById("msg").innerText = "실시간 뉴스 로드 상태 확인";

            // 새로고침 버튼
            //document.getElementById("refresh_news").style.display = 'inline-block';

            // 체크박스 표시  및 함수 정의
            document.getElementById("news-checkbox").style.display = 'block';

            // 가져온 json 데이터 파싱 후 forEach문으로 table 출력
            //console.log(jsonData[1]);
            write_news_data(jsonData[0], jsonData[1]);
            //write_news_data(JSON.parse(jsonData[1]));
        },
        error: function(request, status, error) {
			alert("비동기 요청 중 오류가 발생했습니다.");
			console.log("code : " + request.status);
			console.log("message : " + request.responseText);
			console.log("error : " + error);
		}
	});
}

// 특정 단어를 파란색으로 변경
function highlightText(text) {
    const keywords = ['인하공전', '인하공업전문대학', '전문대학', '인하대', '항공대'];
    keywords.forEach(keyword => {
        const regex = new RegExp(keyword, 'g');
        text = text.replace(regex, `<span style="color: #0049cf;">${keyword}</span>`);
    });
    return text;
}

// html에 작성
function write_news_data(error, result) {
    const container = document.getElementById("news-list");

    result.forEach(function(company, i) {
        //let name = getnewsname(company);
        let name = Object.keys(company);
        if(company[name].length == 0) {
            return;
        }

        // 테이블을 .responsive-container로 감싸기
        const tableId = `table_${i + 1}`;
        let html = `
        <div id="${name}" class="responsive-container">
            <h1>${name}</h1>
            <table class="custom-table" style="visibility:inherit;">
                <thead>
                    <tr>
                        <th class="column-no">No</th>
                        <th class="column-title" scope="col">뉴스 제목</th>
                        <th class="column-date" scope="col">날짜</th>
                    </tr>
                </thead>
                <tbody>
        `;

        for (let i = 0; i < 10; i++) {
            const news = company[name][i];
            if(news == undefined) {
                return;
            }

            html += `
                <tr>
                <td class="column-no">${i + 1}</td>
                <td class="column-title"><a href="${news.link}" target="_blank">${highlightText(news.title)}</a></td>
                <td class="column-date" scope="row">${(news.date)}</td>
                </tr>
            `;
        }

        html += `
            </tbody>
            </table>
            <br>
        </div>
        `;

        container.insertAdjacentHTML('beforeend', html);

        //document.getElementById(name).style.visibility = 'visible';
    });

    // 에러로 받지 못한 데이터 체크 false
    if(error != "") {
        for(let i=0; i<error.length; i++) {
            let name = error[i].name.trim();
            check_newsItem(name);
        }
    }
}

// 임시 카운터
function count_value(time) {
    let what = document.getElementById("msg");

	try {
        var x = setInterval(function() {
			what.innerHTML = "데이터를 가져오는 중입니다... " + time + "초";
			time--;

			if(time<0) {
				clearInterval(x);
				// 메세지 출력
                document.getElementById("msg").innerText = getdate();
			}
		}, 1000);
	} catch (error) {
		console.log(error);
	}
}


// 현재 시간 표시
function getdate() {
    let today = new Date();
    let year = today.getFullYear();
    let month = today.getMonth() + 1;
    let date = today.getDate();
    let day = today.getDay();
    let hours = today.getHours();
    let minutes = today.getMinutes();

    let str = year + "/" + month + "/" + date + " " + hours + ":" + minutes + " 기준 결과 입니다.";

    return str;
}

// 뉴스 이름
function check_newsItem(company) {
    switch(company) {
        case "대학지성IN&OUT":
            document.getElementById("unipress").checked = false; break;
        case "한국대학신문(UNN)":
            document.getElementById("unn").checked = false; break;
        case "유스라인(Usline)":
            document.getElementById("usline").checked = false; break;
        case "대학저널":
            document.getElementById("dhnews").checked = false; break;
        case "베리타스알파":
            document.getElementById("veritas").checked = false; break;
        case "경인일보":
            document.getElementById("kyeongin").checked = false; break;
        case "인천일보":
            document.getElementById("incheonilbo").checked = false; break;
        case "연합뉴스":
            document.getElementById("yna").checked = false; break;
        case "교육부보도자료":
            document.getElementById("moe").checked = false; break;
        case "인천광역시보도자료":
            document.getElementById("incheon").checked = false; break;
        case "교수신문":
            document.getElementById("kyosu").checked = false; break;
        case "한국전문대학교육협의회":
            document.getElementById("kcce").checked = false; break;
        case "조선에듀":
            document.getElementById("chosun").checked = false; break;
        case "네이버통합뉴스(인하공전)":
            document.getElementById("naver").checked = false; break;
    }
}


// 뉴스 체크표시 on off
function toggleCheck(item) {
    if (item.checked) {
        if (item.value == "네이버통합뉴스") {
            document.getElementById("네이버통합뉴스(인하공전)").style.visibility = 'visible';
            document.getElementById("네이버통합뉴스(인하공전)").style.display = 'inline-block';
            document.getElementById("네이버통합뉴스(인하대)").style.visibility = 'visible';
            document.getElementById("네이버통합뉴스(인하대)").style.display = 'inline-block';
            document.getElementById("네이버통합뉴스(항공대)").style.visibility = 'visible';
            document.getElementById("네이버통합뉴스(항공대)").style.display = 'inline-block';
        } else {
            document.getElementById(item.value).style.visibility = 'visible';
            document.getElementById(item.value).style.display = 'inline-block';
        }
    } else {
        if (item.value == "네이버통합뉴스") {
            document.getElementById("네이버통합뉴스(인하공전)").style.visibility = 'hidden';
            document.getElementById("네이버통합뉴스(인하공전)").style.display = 'none';
            document.getElementById("네이버통합뉴스(인하대)").style.visibility = 'hidden';
            document.getElementById("네이버통합뉴스(인하대)").style.display = 'none';
            document.getElementById("네이버통합뉴스(항공대)").style.visibility = 'hidden';
            document.getElementById("네이버통합뉴스(항공대)").style.display = 'none';
        } else {
            document.getElementById(item.value).style.visibility = 'hidden';
            document.getElementById(item.value).style.display = 'none';
        }
    }
}


// 새로고침
$("#refresh_news").click(function() {
    document.getElementById("news-list").innerText = "";
    ajax_get_data();
});



function truncateString(str, maxLength) {
    if (str.length > maxLength) {
        return str.slice(0, maxLength) + "...";
    }
    return str;
}