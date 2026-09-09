/* aiburnclock.org embed: <script src="https://aiburnclock.org/embed.js" data-scope="world|federal" data-state="TX"></script> */
(function(){
  var s=document.currentScript, scope=(s&&s.dataset.scope)||'world', state=s&&s.dataset.state;
  var box=document.createElement('a'); box.href='https://aiburnclock.org/'+(state?('state/'+state.toLowerCase()+'/'):'');
  box.target='_blank'; box.rel='noopener';
  box.style.cssText='display:inline-block;width:300px;box-sizing:border-box;padding:12px 14px;background:#0B0D10;color:#E8E6E1;border:1px solid #262C33;font:12px/1.4 "IBM Plex Mono",Menlo,monospace;text-decoration:none';
  box.innerHTML='<div style="letter-spacing:.08em;text-transform:uppercase;color:#9AA3AD">AI burn clock'+(state?' · '+state.toUpperCase():'')+'</div><div data-v style="font-size:26px;font-weight:600;color:#FF6A00;margin:4px 0">…</div><div style="color:#9AA3AD">burning on avoidable reading since you loaded this page</div>';
  s.parentNode.insertBefore(box,s);
  fetch('https://aiburnclock.org/data.json').then(function(r){return r.json()}).then(function(D){
    var P={};for(var k in D.params)P[k]=D.params[k].default;
    var base = state ? (D.states.filter(function(x){return x.code===state.toUpperCase()})[0]||{ai_fy2026:0}).ai_fy2026 : (scope==='federal'?D.federal_ai.fy2026_annualised:D.world_ai_2026);
    var perSec=base*P.inference_share*P.agent_share*P.overhead/31557600, t0=Date.now(), el=box.querySelector('[data-v]');
    function fmt(n){var a=Math.abs(n),u=[[1e12,'T'],[1e9,'B'],[1e6,'M'],[1e3,'K']];for(var i=0;i<u.length;i++)if(a>=u[i][0])return '$'+(n/u[i][0]).toFixed(2)+u[i][1];return '$'+n.toFixed(2)}
    (function tick(){el.textContent=fmt(perSec*(Date.now()-t0)/1000);requestAnimationFrame(tick)})();
  }).catch(function(){});
})();
