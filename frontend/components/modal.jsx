export default function Modal() {
  return (
    <div className="modal fade" id="modal" tabIndex="-1" role="dialog" aria-labelledby="myModalLabel"
         aria-hidden="true">
      <div className="modal-dialog modal-lg" role="document">
        {/* Content */}
        <div className="modal-content modal-top">
          <div className="modal-header">
            {/* <h5 class="modal-title" id="exampleModalLabel">Modal title</h5> */}
            <button type="button" className="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          {/* Body */}
          <div className="modal-body" />
          <div className="modal-footer">
            <button type="button" className="btn" data-dismiss="modal">Close</button>
          </div>
        </div>
        {/* /.Content */}
      </div>
    </div>
  );
}