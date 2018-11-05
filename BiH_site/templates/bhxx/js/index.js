

$(document).ready(function(){
        $(window).scroll(function() {
            let s=document.documentElement.scrollTop + document.body.scrollTop
            if (s > 600 && s<1500) {
                    $('.top').animate({
                        top:'-300px'
                    },1500)
                    $('.bottom').animate({
                        top:'600px'
                    },1500)
                    $('.showTeam').delay(1500).animate({
                        opacity:'1'
                    },1500)
            }
        })
})






