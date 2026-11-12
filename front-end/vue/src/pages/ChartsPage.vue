<script setup lang="ts">
import { computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import VChart from "vue-echarts";
import type { EChartsOption } from "echarts";
import { use } from "echarts/core";
import { PieChart } from "echarts/charts";
import { TooltipComponent, LegendComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import { api } from "@/api/http";
use([PieChart,TooltipComponent,LegendComponent,CanvasRenderer]);
interface Dataset{ id:string;title:string;chartType:string;description:string|null;points:{label:string;value:number}[] }
const {data,isPending,isError}=useQuery({queryKey:["charts","chart-datasets"],queryFn:()=>api.get<{datasets:Dataset[]}>("/demo/charts")});
const datasets=computed(()=>data.value?.datasets.filter(d=>["pie","donut","radial"].includes(d.chartType))??[]);
function option(d:Dataset):EChartsOption{return{tooltip:{trigger:"item"},legend:{bottom:0},series:[{type:"pie",radius:d.chartType==="donut"?["48%","72%"]:d.chartType==="radial"?["25%","70%"]:"68%",roseType:d.chartType==="radial"?"radius":undefined,data:d.points.map(p=>({name:p.label,value:p.value})),label:{show:true}}]};}
</script>
<template><div><h1 class="page-title">Charts</h1><p class="muted">Pie, donut and radial chart variants for share-of-total and progress data — live from the backend.</p><p v-if="isPending" class="muted">Loading…</p><p v-else-if="isError" class="error">Failed to load chart data.</p><div v-else class="grid grid-3" style="margin-top:20px"><section v-for="d in datasets" :key="d.id" class="card"><h2 style="font-size:16px;margin:0">{{d.title}}</h2><VChart :option="option(d)" autoresize style="height:270px"/><p v-if="d.description" class="muted">{{d.description}}</p></section></div></div></template>