<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useQueries } from "@tanstack/vue-query";
import * as L from "leaflet";
import { api } from "@/api/http";
import { getHeatmapColor, getProjectCountTier, tierColors } from "@/utils/mapStyles";

interface StateMetric { id:string; stateCode:string; stateName:string; projectCount:number; activityIntensity:number }
interface District { type:"Feature"; properties:{district:string;st_nm:string;st_code:string}; geometry:GeoJSON.Geometry }
const queries=useQueries({queries:[
 {queryKey:["dashboard","districts"],queryFn:async()=>{const r=await fetch("/data/india-districts.geojson");if(!r.ok)throw new Error("District boundaries unavailable");return r.json() as Promise<GeoJSON.FeatureCollection>}},
 {queryKey:["dashboard","mask"],queryFn:async()=>{const r=await fetch("/data/india-mask.geojson");if(!r.ok)throw new Error("Map mask unavailable");return r.json() as Promise<GeoJSON.FeatureCollection>}},
 {queryKey:["dashboard","state-metrics"],queryFn:()=>api.get<{states:StateMetric[]}>("/demo/map/states")},
]});
const metrics=computed(()=>queries.value[2]?.data?.states??[]);
const totalProjects=computed(()=>metrics.value.reduce((sum,item)=>sum+item.projectCount,0));
const maxActivity=computed(()=>Math.max(1,...metrics.value.map(item=>item.activityIntensity)));
const mapOne=ref<HTMLElement|null>(null),mapTwo=ref<HTMLElement|null>(null);
let projectMap:L.Map|undefined,activityMap:L.Map|undefined;
const mapError=ref("");
function drawMap(target:HTMLElement,kind:"projects"|"activity"){
 const map=L.map(target,{scrollWheelZoom:false}).setView([22.97,78.65],4);
 L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:"© OpenStreetMap"}).addTo(map);
 const mask=queries.value[1]?.data as GeoJSON.FeatureCollection|undefined;
 if(mask)L.geoJSON(mask as never,{style:{color:"#fff",weight:0,fillColor:"#fff",fillOpacity:1,interactive:false}}).addTo(map);
 const features=queries.value[0]?.data?.features as District[]|undefined;
 const stateMap=new Map(metrics.value.map(item=>[item.stateCode,item]));
 if(features){
  const layer=L.geoJSON(features as never,{style:(feature)=>{
   const props=(feature as unknown as District).properties;
   const metric=stateMap.get(props.st_code);
   return {color:"#fff",weight:.65,fillOpacity:.82,fillColor:kind==="projects"?(tierColors[getProjectCountTier(metric?.projectCount??0)]??"#e2e8f0"):getHeatmapColor(metric?.activityIntensity??0,maxActivity.value)};
  },onEachFeature:(feature,layer)=>{
   const props=(feature as unknown as District).properties;
   const metric=stateMap.get(props.st_code);
   const label=kind==="projects"?"Projects":"Activity";
   const value=kind==="projects"?(metric?.projectCount??0):(metric?.activityIntensity??0);
   layer.bindTooltip("<strong>"+String(props.st_nm)+"</strong><br/>"+(props.district?"District: "+String(props.district)+"<br/>":"")+label+": "+String(value));
  }}).addTo(map);
  try{map.fitBounds(layer.getBounds(),{padding:[8,8]});}catch{/* Empty geojson */}
 }
 return map;
}
function seededRandom(seed:string):()=>number{
 let hash=0;for(let i=0;i<seed.length;i++){hash=(hash<<5)-hash+seed.charCodeAt(i);hash|=0;}
 let state=hash;
 return ()=>{state|=0;state=(state+0x6d2b79f5)|0;let t=Math.imul(state^(state>>>15),1|state);t=(t+Math.imul(t^(t>>>7),61|t))^t;return((t^(t>>>14))>>>0)/4294967296;};
}
function sampleStat(seed:string,base:number,spread:number){return Math.round(base+seededRandom(seed)()*spread);}
const activeUsers=sampleStat("overview-active-users",800,900);
const totalRequests=sampleStat("overview-total-requests",2500,2000);
onMounted(async()=>{
 try{
  await Promise.all(queries.value.map(q=>q.suspense()));
  if(mapOne.value)projectMap=drawMap(mapOne.value,"projects");
  if(mapTwo.value)activityMap=drawMap(mapTwo.value,"activity");
 }catch{mapError.value="Failed to load dashboard map data.";}
});
onBeforeUnmount(()=>{projectMap?.remove();activityMap?.remove();});
const dateRange=new Intl.DateTimeFormat("en-US",{day:"2-digit",month:"short"}).format(new Date());
const projectLegend=[["100+","#7a0002"],["50–100","#c10003"],["20–50","#e2434b"],["5–20","#f0989c"],["1–5","#fbd9da"],["0","#f1f5f9"]];
</script>
<template>
 <div>
  <div class="toolbar" style="margin-top:0"><div><h1 class="page-title">Dashboard</h1><p class="muted">Visualize project insights across India</p></div><div style="display:flex;gap:8px;align-items:center"><select aria-label="Region filter" class="filter-select"><option>All India</option></select><span class="pill">Last 7 days · {{dateRange}}</span></div></div>
  <div class="grid grid-3" style="margin-bottom:20px">
   <div class="card"><span class="muted">Total Projects</span><div class="stat-value">{{totalProjects.toLocaleString("en-US")}}</div><small class="muted">Across states and districts</small></div>
   <div class="card"><span class="muted">Active Users</span><div class="stat-value">{{activeUsers.toLocaleString("en-US")}}</div><small class="muted">Illustrative overview metric</small></div>
   <div class="card"><span class="muted">Total Requests</span><div class="stat-value">{{totalRequests.toLocaleString("en-US")}}</div><small class="muted">Illustrative overview metric</small></div>
  </div>
  <p v-if="mapError" class="error">{{mapError}}</p>
  <div class="grid grid-2">
   <section class="card"><div class="toolbar" style="margin:0 0 12px"><div><h2 style="margin:0 0 4px;font-size:16px">India Map – Project Distribution</h2><p class="muted" style="margin:0">Project distribution by state and district</p></div><select aria-label="State filter" class="filter-select"><option>All States</option></select></div><div ref="mapOne" class="map"></div><div class="legend-row"><span v-for="item in projectLegend" :key="item[0]"><i :style="{background:item[1]}"></i>{{item[0]}}</span></div><p class="muted" style="margin-top:8px">Darker red indicates a higher project count.</p></section>
   <section class="card"><div class="toolbar" style="margin:0 0 12px"><div><h2 style="margin:0 0 4px;font-size:16px">India Map – Activity Intensity</h2><p class="muted" style="margin:0">Activity intensity heatmap</p></div><select aria-label="State filter" class="filter-select"><option>All States</option></select></div><div ref="mapTwo" class="map"></div><div class="heat-legend"><span>Low</span><i></i><span>High</span></div><p class="muted" style="margin-top:8px">Blue indicates lower intensity; red indicates higher intensity.</p></section>
  </div>
 </div>
</template>
<style scoped>.filter-select{padding:7px 9px;border:1px solid #cbd5e1;border-radius:7px;background:white;font-size:12px}.legend-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}.legend-row span{display:flex;align-items:center;gap:4px;font-size:10px;color:#64748b}.legend-row i{width:10px;height:10px;border-radius:2px}.heat-legend{display:flex;align-items:center;gap:8px;margin-top:12px;font-size:10px;color:#64748b}.heat-legend i{height:9px;flex:1;border-radius:5px;background:linear-gradient(to right,#2563eb,#22d3ee,#4ade80,#facc15,#ef4444)}</style>