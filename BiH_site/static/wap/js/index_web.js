


var sildeShow=document.getElementById("sildeShow").children
var sildeShow_hd_border=document.getElementsByName("sildeShow_hd_border")
var sildeShow_hd_icon=document.getElementsByName("sildeShow_hd_icon")
for(var s=0;s<sildeShow.length;s++){
    sildeShow[s].num=s;
    sildeShow[s].onclick=function () {
        if(this.className =='opens'){
            this.className='sildeShow_hd';
            //this.style.heigth="42px"
            sildeShow_hd_border[this.num].style.display=""
            sildeShow_hd_icon[this.num].style.transform="rotate(0deg)"
        }else  if(this.className == 'sildeShow_hd'){
            for(var i=0;i<sildeShow.length;i++){
                sildeShow[i].className='sildeShow_hd'
                //sildeShow[i].style.height="42px"
                sildeShow_hd_border[i].style.display=""
                sildeShow_hd_icon[i].style.transform="rotate(0deg)"

            }
            this.className="opens"
            sildeShow_hd_border[this.num].style.display="block"
            sildeShow_hd_icon[this.num].style.transform="rotate(360deg)"
         }

    }
}




