/*
// 검색 버튼 클릭 이벤트 리스너
document.getElementById("searchItem").addEventListener("click", function() {
    let search = document.getElementById("search")

    if(search.value == "") {
        alert("검색할 키워드를 입력해주세요!");
        search.focus();
        return;
    }

    $.ajax({
    	url:"/searchItem",
        type:"post",
        dataType:"json",
        data:{"search" : search.value},
        success: function(data){
			//console.log(data);
			if(data == 1 || data == "1") {
			    alert("외부 API 연동에 실패하였습니다.");
			    return;
			}

            // 이전 데이터 초기화
            document.querySelector("#news_table tbody").textContent = "";

            let table = document.getElementById("news_table");
            table.style.visibility = 'visible';

            // 데이터 가져와서 출력
            var count = 0;
			$(data).each(function() {
			    count += 1;
			    let date = this.date;
			    let link = this.link;
			    let title = this.title;

			    writeTablePage(count, date, link, title);
			});

        },
        error: function(request, status, error) {
			alert("비동기 요청 중 오류가 발생했습니다.");
			console.log("code : " + request.status);
			console.log("message : " + request.responseText);
			console.log("error : " + error);
		}
	});
});


// enter키 이벤트
function enterkey() {
    if (window.event.keyCode == 13) {
        document.getElementById("searchItem").click();
    }
}


// 가져온 데이터 HTML 출력
function writeTablePage(count, date, link, title) {
    // 특정 단어를 파란색으로 변경
    function highlightText(text) {
<<<<<<< HEAD
        const keywords = ['인하공전', '인하공업전문대학', '전문대학' ,'인하대', '항공대'];
=======
        const keywords = ['인하공전', '인하공업전문대학', '전문대학', '인하대', '항공대];
>>>>>>> 989b874d9c68d1bcc0ac13de57355c92a3d2cf9a
        keywords.forEach(keyword => {
            const regex = new RegExp(keyword, 'g');
            text = text.replace(regex, `<b><span style="color: #0049cf;">${keyword}</span></b>`);
        });
        return text;
    }

    const html = `
        <tr>
            <td class="column-no">${count}</td>
            <td class="column-title"><a href="${link}" target="_blank">${highlightText(title)}</a></td>
            <td class="column-date" scope="row">${date.substr(5)}</td>
        </tr>
    `;

    let tbodywhere = document.querySelector("#news_table tbody");
    tbodywhere.insertAdjacentHTML('beforeend', html);
}
*/