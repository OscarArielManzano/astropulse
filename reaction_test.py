"""Test de reacción tipo PVT: fondo azul, al ponerse rojo hacer clic. Ayuda a la decisión, no diagnóstico."""
import streamlit.components.v1 as components

N_TRIALS = 20   # con 20 ensayos, cada lapso vale 5 puntos porcentuales
LAPSE_MS = 500  # umbral de lapso (Foundation Document, sección 7)

HTML = """
<div id="box" style="height:280px;background:#1e5eff;color:#fff;display:flex;align-items:center;
justify-content:center;font:22px sans-serif;cursor:pointer;user-select:none">Clic para iniciar</div>
<p id="out" style="font:16px sans-serif"></p>
<script>
const N=__N__, LAPSE=__LAPSE__;
let state="idle", trial=0, rts=[], fs=0, t0=0, timer=null;
const box=document.getElementById("box"), out=document.getElementById("out");
function nextTrial(){
  state="wait"; box.style.background="#1e5eff"; box.textContent="Wait for the red... ("+(trial+1)+"/"+N+")";
  timer=setTimeout(()=>{state="go"; box.style.background="#e02020"; box.textContent="¡CLIC!"; t0=performance.now();},
                   2000+Math.random()*4000);
}
function finish(){
  state="done"; box.style.background="#1e5eff"; box.textContent="Listo. Clic para repetir";
  const mean=rts.reduce((a,b)=>a+b,0)/rts.length;
  const lapses=rts.filter(r=>r>LAPSE).length;
  out.innerHTML="<b>Tiempo medio:</b> "+mean.toFixed(0)+" ms<br><b>Lapsos (&gt;"+LAPSE+" ms):</b> "+
    (100*lapses/N).toFixed(1)+" %<br><b>Salidas en falso:</b> "+fs;
}
box.addEventListener("mousedown",()=>{
  if(state==="idle"||state==="done"){trial=0;rts=[];fs=0;out.textContent="";nextTrial();}
  else if(state==="wait"){clearTimeout(timer);fs++;state="pause";box.textContent="Muy pronto. Espera...";setTimeout(nextTrial,1000);}
  else if(state==="go"){
    const rt=performance.now()-t0; rts.push(rt); trial++; state="pause";
    if(trial>=N) finish(); else {box.textContent=Math.round(rt)+" ms"; setTimeout(nextTrial,800);}
  }
});
</script>
""".replace("__N__", str(N_TRIALS)).replace("__LAPSE__", str(LAPSE_MS))


def render_reaction_test(height=420):
    components.html(HTML, height=height)