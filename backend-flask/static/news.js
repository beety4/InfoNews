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

// 특정 단어를 파란색으로 변경
function highlightText(text) {
    const keywords = ['인하공전', '인하공업전문대학', '전문대학'];
    keywords.forEach(keyword => {
        const regex = new RegExp(keyword, 'g');
        text = text.replace(regex, `<span style="color: #0049cf;">${keyword}</span>`);
    });
    return text;
}

// html에 작성
function write_news_data(result) {
    const container = document.getElementById("news-list");

    const customOrder = ["한국전문대학교육협의회", "교육부보도자료",
        "인천광역시보도자료", "베리타스알파", "한국대학신문(UNN)", "대학저널",
        "유스라인(Usline)", "교수신문", "대학지성IN&OUT", "조선에듀", "연합뉴스"];

    result.sort((a, b) => {
        const nameA = getnewsname(a);
        const nameB = getnewsname(b);
        const indexA = customOrder.indexOf(nameA);
        const indexB = customOrder.indexOf(nameB);
        return indexA - indexB;
    });

    result.forEach(function(company, i) {
        let name = getnewsname(company);
        if(name == "사이트에러") {
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

        for (let i = 0; i < company.length && i < 10; i++) {
            const news = company[i];
            html += `
                <tr>
                <td class="column-no">${i + 1}</td>
                <td class="column-title"><a href="${news.link}" target="_blank">${highlightText(news.title)}</a></td>
                <td class="column-date" scope="row">${(news.date).substr(5)}</td>
                </tr>
            `;
        }

        html += `
            </tbody>
            </table>
        </div><br>
        `;

        container.insertAdjacentHTML('beforeend', html);

        //document.getElementById(name).style.visibility = 'visible';
    });
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
function getnewsname(company) {
    try {
        if(company[0].link.includes("unipress.co.kr")) {
            return "대학지성IN&OUT";
        } else if(company[0].link.includes("news.unn.net")) {
            return "한국대학신문(UNN)";
        } else if(company[0].link.includes("usline.kr")) {
            return "유스라인(Usline)";
        } else if(company[0].link.includes("dhnews.co.kr")) {
            return "대학저널";
        } else if(company[0].link.includes("veritas-a.com")) {
            return "베리타스알파";
        } else if(company[0].link.includes("yna.co.kr")) {
            return "연합뉴스";
        } else if(company[0].link.includes("moe.go.kr")) {
            return "교육부보도자료";
        } else if(company[0].link.includes("incheon.go.kr")) {
            return "인천광역시보도자료";
        } else if(company[0].link.includes("kyosu.net")) {
            return "교수신문";
        } else if(company[0].link.includes("kcce.or.kr")) {
            return "한국전문대학교육협의회";
        } else if(company[0].link.includes("edu.chosun.com")) {
            return "조선에듀";
        } else {
            return "네이버통합뉴스";
        }
    } catch (e) {
        return "사이트에러"
    }
}


// 뉴스 체크표시 on off
function toggleCheck(item) {
    if (item.checked) {
        document.getElementById(item.value).style.visibility = 'visible';
        document.getElementById(item.value).style.display = 'inline-block';
    } else {
        document.getElementById(item.value).style.visibility = 'hidden';
        document.getElementById(item.value).style.display = 'none';
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