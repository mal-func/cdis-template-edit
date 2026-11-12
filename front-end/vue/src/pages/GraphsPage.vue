<script setup lang="ts">
import { computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import VChart from "vue-echarts";
import type { EChartsOption } from "echarts";
import { use } from "echarts/core";
import { BarChart, LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import { api } from "@/api/http";
use([BarChart,LineChart,GridComponent,TooltipComponent,LegendComponent,CanvasRenderer]);
interface Dataset{ id:string;slug:string;title:string;chartType:string;description:string|null;points:{label:string;series:string|null;value:number}[] }
const {data,isPending,isError}=useQuery({queryKey:["graphs","chart-datasets"],queryFn:()=>api.get<{datasets:Dataset[]}>("/demo/charts")});
const datasets=computed(()=>data.value?.datasets.filter(d=>["bar","line","area"].includes(d.chartType))??[]);
function option(dataset:Dataset):EChartsOption{
 const labels=[...new Set(dataset.points.map(p=>p.label))],series=[...new Set(dataset.points.map(p=>p.series??"Value"))];
 return {tooltip:{trigger:"axis"},legend:{bottom:0},grid:{left:42,right:18,top:20,bottom:42},xAxis:{type:"category",data:labels},yAxis:{type:"value"},series:series.map(name=>({name,type:(dataset.chartType==="area"?"line":dataset.chartType) as "bar"|"line",smooth:dataset.chartType!=="bar",areaStyle:dataset.chartType==="area"?{}:undefined,data:labels.map(label=>dataset.points.find(p=>p.label===label&&(p.series??"Value")===name)?.value??0)}))};
}
</script>
<template><div><h1 class="page-title">Graphs</h1><p class="muted">Bar, line and area chart variants, including grouped and multi-series data, fetched live from the backend.</p><p v-if="isPending" class="muted">Loading…</p><p v-else-if="isError" class="error">Failed to load chart data.</p><div v-else class="grid grid-2" style="margin-top:20px"><section v-for="d in datasets" :key="d.id" class="card"><h2 style="font-size:16px;margin:0 0 12px">{{d.title}}</h2><VChart :option="option(d)" autoresize style="height:300px"/><p v-if="d.description" class="muted">{{d.description}}</p></section></div></div></template>