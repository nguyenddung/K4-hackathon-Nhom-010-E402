import Icon from '../Icon'

export default function UploadModal({ onClose, onSubmit, uploading, uploadError, uploadJobId, jobList, dragActive, handleDrag, handleDrop, selectedFile, setSelectedFile }) {
  return (
    <div className="fixed inset-0 z-30 bg-[#132a246b] backdrop-blur-[2px] grid place-items-center p-[20px]">
      <div className="relative w rounded-[10px] bg-paper p-[28px] shadow-[0_24px_70px_#152d2440]">
        <button className="absolute right-[16px] top-[12px] border-0 bg-transparent text-[#7a8480] text-[22px]" onClick={onClose}>×</button>
        <p className="text-xs uppercase tracking-widest text-slate-500 m-[0_0_8px]">DATA INGESTION</p>
        <h2 className="font-serif text-2xl font-semibold m-[0_0_8px]">Tải CV ứng viên</h2>
        <p className="text-sm text-slate-700 leading-6 m-0 mb-[18px]">Hệ thống hỗ trợ PDF, DOCX (tối đa 5MB). Dữ liệu được mã hóa và không dùng để train public AI.</p>
        <form onSubmit={onSubmit}>
          <div className="grid grid-cols-2 max-[650px]:grid-cols-1 gap-[12px]">
            <label className="grid gap-[6px] text-sm font-semibold text-[#4c5753] col-span-full">Ứng tuyển cho vị trí
              <select className="w-full border border-[#cfd4cf] rounded-[6px] bg-white p-[10px] text-ink outline-forest text-sm" name="jobId" defaultValue={uploadJobId}>
                {jobList.map(job => <option key={job.id} value={job.id}>{job.title} · {job.department}</option>)}
              </select>
            </label>
            <label className="grid gap-[6px] text-sm font-semibold text-[#4c5753]">Họ và tên
              <input className="w-full border border-[#cfd4cf] rounded-[6px] bg-white p-[10px] text-ink outline-forest text-sm" name="name" required placeholder="Tên ứng viên" />
            </label>
            <label className="grid gap-[6px] text-sm font-semibold text-[#4c5753]">File CV
              <div
                className={`min-h-[112px] border border-dashed rounded-[7px] flex flex-col items-center justify-center gap-[5px] cursor-pointer transition-[.2s] ${dragActive ? 'border-[2px] border-forest bg-[#e0efe6]' : 'border-[#9db4aa] bg-[#f3f7f3] hover:border-forest hover:bg-[#edf4ef]'} text-forest`}
                onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
                onClick={() => document.getElementById('cv-upload-input').click()}
              >
                <input id="cv-upload-input" className="absolute w-[1px] h-[1px] opacity-0" name="cv" type="file" accept=".pdf,.doc,.docx" required={!selectedFile} onChange={e => e.target.files[0] && setSelectedFile(e.target.files[0])} />
                <span className="w-[28px] h-[28px] rounded-full grid place-items-center bg-[#dcebe3] font-bold">↑</span>
                <b className="text-sm font-medium">{selectedFile ? selectedFile.name : 'Kéo thả hoặc click để chọn file'}</b>
                {!selectedFile && <small className="text-xs text-slate-500">Hỗ trợ PDF, DOCX dưới 5MB</small>}
              </div>
            </label>
          </div>
          {uploadError && <div className="mt-[12px] p-[9px_10px] rounded-[5px] bg-[#f8e8e4] text-[#9d4035] text-sm font-medium">{uploadError}</div>}
          <div className="mt-[12px] p-[9px_10px] flex items-center gap-[8px] rounded-[5px] bg-[#eaf2ed] text-[#557067] text-xs font-medium">
            <div className="flex-none text-forest"><Icon name="shield" /></div> Data Privacy: CV chỉ được phân tích cho mục đích tuyển dụng nội bộ.
          </div>
          <div className="flex justify-end gap-[8px] mt-[18px]">
            <button className="border border-[#c9cfca] bg-paper text-[#48534f] rounded-[6px] p-[10px_14px] text-sm font-medium" type="button" onClick={onClose} disabled={uploading}>Hủy</button>
            <button className="border-0 bg-forest text-white rounded-[6px] p-[11px_15px] text-sm font-medium shadow-[0_1px_2px_#123d3525] disabled:opacity-65 disabled:cursor-wait" type="submit" disabled={uploading}>{uploading ? 'Đang tải lên...' : 'Upload & Xử lý'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}
