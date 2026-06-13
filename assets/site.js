
/* Tanapat website interactions (no framework) */
const lb=document.getElementById('lb'),lbImg=document.getElementById('lb-img'),lbCap=document.getElementById('lb-cap');
function openLB(src,cap){lbImg.src=src;lbCap.textContent=cap||'';lb.classList.add('show');document.body.style.overflow='hidden';}
function closeLB(){lb.classList.remove('show');lbImg.src='';document.body.style.overflow='';}
if(lb){lb.addEventListener('click',closeLB);document.addEventListener('keydown',e=>{if(e.key==='Escape')closeLB();});}
document.querySelectorAll('[data-lb]').forEach(el=>el.addEventListener('click',()=>openLB(el.dataset.lb,el.dataset.cap)));
document.querySelectorAll('.qa button').forEach(b=>b.addEventListener('click',()=>{
  const qa=b.parentElement,ans=qa.querySelector('.ans');
  const open=qa.classList.toggle('open');ans.style.maxHeight=open?ans.scrollHeight+'px':0;}));
const burger=document.getElementById('burger');
if(burger)burger.addEventListener('click',()=>document.getElementById('menu').classList.toggle('open'));
const yr=document.getElementById('yr');if(yr)yr.textContent=new Date().getFullYear();
const obs=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');obs.unobserve(e.target);}}),{threshold:.08});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
document.querySelectorAll('[data-cnt]').forEach(el=>{
  const end=Number(el.dataset.cnt);let started=false;
  const io=new IntersectionObserver(es=>es.forEach(e=>{
    if(e.isIntersecting&&!started){started=true;io.disconnect();
      const t0=performance.now(),dur=1400;
      const step=now=>{const p=Math.min((now-t0)/dur,1);
        el.textContent=Math.round(end*(1-Math.pow(1-p,3))).toLocaleString();
        if(p<1)requestAnimationFrame(step);};
      requestAnimationFrame(step);}}));
  io.observe(el);});
/* article filter (articles.html) */
const grid=document.getElementById('art-grid');
if(grid){
  const q=document.getElementById('art-q'),chips=document.querySelectorAll('.chip'),cnt=document.getElementById('art-count');
  let cat='ทั้งหมด';
  function apply(){
    const qq=(q.value||'').trim().toLowerCase();let n=0;
    grid.querySelectorAll('.acard').forEach(c=>{
      const ok=(cat==='ทั้งหมด'||c.dataset.cat===cat)&&(!qq||c.dataset.text.includes(qq));
      c.style.display=ok?'':'none';if(ok)n++;});
    cnt.textContent='พบ '+n+' บทความ';}
  q.addEventListener('input',apply);
  chips.forEach(c=>c.addEventListener('click',()=>{cat=c.dataset.cat;
    chips.forEach(x=>x.classList.toggle('on',x===c));apply();}));
  apply();
}
