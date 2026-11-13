<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { api } from "@/api/http";
interface Dataset{id:string;slug:string;title:string;description:string|null;rows:Record<string,unknown>[]}
const {data,isPending,isError}=useQuery({queryKey:["tables","table-datasets"],queryFn:()=>api.get<{datasets:Dataset[]}>("/demo/tables")});
const search=ref(""),sortKeys=ref<Record<string,string>>({}),sortDesc=ref<Record<string,boolean>>({}),pages=ref<Record<string,number>>({});
const PAGE_SIZE=10;
const datasets=computed(()=>data.value?.datasets??[]);
watch(search,()=>{pages.value={};});
function columns(dataset:Dataset){return Object.keys(dataset.rows[0]??{});}
function filteredRows(dataset:Dataset){return dataset.rows.filter(row=>JSON.stringify(Object.values(row)).toLowerCase().includes(search.value.toLowerCase()));}
function sortedRows(dataset:Dataset){const rows=[...filteredRows(dataset)],key=sortKeys.value[dataset.slug];if(key)rows.sort((a,b)=>String(a[key]??"").localeCompare(String(b[key]??""),undefined,{numeric:true,sensitivity:"base"})*(sortDesc.value[dataset.slug]?-1:1));return rows;}
function visibleRows(dataset:Dataset){const start=(pages.value[dataset.slug]??0)*PAGE_SIZE;return sortedRows(dataset).slice(start,start+PAGE_SIZE);}
function pageCount(dataset:Dataset){return Math.max(1,Math.ceil(filteredRows(dataset).length/PAGE_SIZE));}
function toggleSort(dataset:Dataset,column:string){if(sortKeys.value[dataset.slug]===column)sortDesc.value[dataset.slug]=!sortDesc.value[dataset.slug];else{sortKeys.value[dataset.slug]=column;sortDesc.value[dataset.slug]=false;}pages.value[dataset.slug]=0;}
function display(value:unknown){return typeof value==="object"&&value!==null?JSON.stringify(value):String(value??"");}
function changePage(slug:string,delta:number){const dataset=datasets.value.find(d=>d.slug===slug);if(!dataset)return;pages.value[slug]=Math.max(0,Math.min(pageCount(dataset)-1,(pages.value[slug]??0)+delta));}
</script>
<template>
  <div>
    <h1 class="page-title">
      Table
    </h1><p class="muted">
      Reusable data tables with sortable columns, global search and pagination — live from the backend.
    </p>
    <div class="toolbar">
      <input
        v-model="search"
        placeholder="Search all tables…"
        style="padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;width:min(100%,320px)"
      >
    </div>
    <p
      v-if="isPending"
      class="muted"
    >
      Loading…
    </p><p
      v-else-if="isError"
      class="error"
    >
      Failed to load table data.
    </p>
    <div
      v-else
      class="grid"
      style="margin-top:18px"
    >
      <section
        v-for="dataset in datasets"
        :key="dataset.id"
        class="card"
      >
        <h2 style="font-size:16px;margin:0 0 4px">
          {{ dataset.title }}
        </h2><p class="muted">
          {{ dataset.description }}
        </p><div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th
                  v-for="column in columns(dataset)"
                  :key="column"
                >
                  <button
                    class="sort-button"
                    @click="toggleSort(dataset,column)"
                  >
                    {{ column }} <span>{{ sortKeys[dataset.slug]===column?(sortDesc[dataset.slug]?"↓":"↑"):"↕" }}</span>
                  </button>
                </th>
              </tr>
            </thead><tbody>
              <tr
                v-for="(row,index) in visibleRows(dataset)"
                :key="index"
              >
                <td
                  v-for="column in columns(dataset)"
                  :key="column"
                >
                  {{ display(row[column]) }}
                </td>
              </tr><tr v-if="!sortedRows(dataset).length">
                <td
                  :colspan="Math.max(columns(dataset).length,1)"
                  class="muted"
                >
                  No matching rows.
                </td>
              </tr>
            </tbody>
          </table>
        </div><div class="table-footer">
          <small class="muted">{{ filteredRows(dataset).length }} rows · Page {{ (pages[dataset.slug]??0)+1 }} of {{ pageCount(dataset) }}</small><div style="display:flex;gap:6px">
            <button
              class="btn btn-secondary"
              :disabled="(pages[dataset.slug]??0)===0"
              @click="changePage(dataset.slug,-1)"
            >
              Previous
            </button><button
              class="btn btn-secondary"
              :disabled="(pages[dataset.slug]??0)+1>=pageCount(dataset)"
              @click="changePage(dataset.slug,1)"
            >
              Next
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
<style scoped>.sort-button{border:0;background:transparent;color:inherit;font-weight:650;padding:0}.sort-button span{color:#94a3b8}.table-footer{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:12px}</style>