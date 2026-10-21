// SPDX-License-Identifier: MIT
// DualSpan KWin Plasma 6: spans normal windows (not virtual displays).
var dualSpanSaved = [];
function entry(w) { for (var i=0;i<dualSpanSaved.length;i++) if(dualSpanSaved[i].window===w)return i; return -1; }
function bounds(a,b) {
 var x=Math.min(a.x,b.x),y=Math.min(a.y,b.y);
 return Qt.rect(x,y,Math.max(a.x+a.width,b.x+b.width)-x,Math.max(a.y+a.height,b.y+b.height)-y);
}
function screensFor(w) {
 var screens=workspace.screens;
 if (!screens || screens.length<2)return null;
 if (screens.length===2)return [screens[0],screens[1]];
 var first=w.output||workspace.activeScreen||screens[0], g=first.geometry;
 var cx=g.x+g.width/2,cy=g.y+g.height/2,second=null,dist=Infinity;
 for(var i=0;i<screens.length;i++){
  var other=screens[i];if(other===first)continue;
  var r=other.geometry,dx=r.x+r.width/2-cx,dy=r.y+r.height/2-cy,d=dx*dx+dy*dy;
  if(d<dist){dist=d;second=other;}
 }
 return second?[first,second]:null;
}
function span() {
 var w=workspace.activeWindow;
 if(!w||!w.normalWindow||!w.resizeable||entry(w)>=0)return;
 var pair=screensFor(w);if(!pair)return;
 var r=w.frameGeometry;
 var prior={window:w,geometry:Qt.rect(r.x,r.y,r.width,r.height),fullScreen:Boolean(w.fullScreen)};
 try {
  if(w.fullScreen)w.fullScreen=false;
  w.setMaximize(false,false);
  w.frameGeometry=bounds(pair[0].geometry,pair[1].geometry);
  dualSpanSaved.push(prior);
 } catch(e) {
  print("DualSpan failed: "+String(e));
  try {w.frameGeometry=prior.geometry;}catch(_e){}
 }
}
function restore() {
 var w=workspace.activeWindow;if(!w)return;
 var i=entry(w);if(i<0)return;
 var prior=dualSpanSaved[i];dualSpanSaved.splice(i,1);
 try {
  w.setMaximize(false,false);
  w.frameGeometry=prior.geometry;
  if(prior.fullScreen)w.fullScreen=true;
 } catch(e){print("DualSpan restore failed: "+String(e));}
}
registerShortcut("dualspan-apply","DualSpan: Span active window","Meta+Alt+S",span);
registerShortcut("dualspan-restore","DualSpan: Restore active window","Meta+Alt+R",restore);
workspace.windowRemoved.connect(function(w){var i=entry(w);if(i>=0)dualSpanSaved.splice(i,1);});
