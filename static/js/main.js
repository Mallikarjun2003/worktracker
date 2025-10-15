document.addEventListener('DOMContentLoaded', ()=>{
  // Auto-focus first input on index
  const txt = document.querySelector('input[name="card_no"]');
  if(txt) txt.focus();

  // Flash success when '?ok=1' in URL
  if(location.search.indexOf('ok=1')!==-1){
    const el = document.createElement('div');
    el.className='toast'; el.textContent='Saved ✓';
    Object.assign(el.style,{position:'fixed',right:'20px',bottom:'20px',background:'#04202a',color:'#bfffe0',padding:'10px 14px',borderRadius:'10px',boxShadow:'0 6px 20px rgba(2,6,23,0.6)'});
    document.body.appendChild(el);
    setTimeout(()=>el.style.opacity='0',2400); setTimeout(()=>el.remove(),3000);
  }
});
