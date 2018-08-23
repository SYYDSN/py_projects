var my_modal = `<div class="modal fade bs-example-modal-sm" tabindex="-1" role="dialog" aria-labelledby="mySmallModalLabel"  aria-hidden=”true” data-backdrop=”static”>
<div class="modal-dialog modal-sm" role="document">
  <div class="modal-content">
        <div class="weui-loadmore">
                <i class="weui-loading"></i>
                <span class="weui-loadmore__tips">正在上传，请稍后</span>
        </div>
  </div>
</div>
</div>`;
$('.container-fluid').after(my_modal);
