import {useState} from "react";
import stocks from "../data/stocks";


function StockSelector(){

const [selected,setSelected]=useState(stocks[0]);


return (

<div className="
bg-slate-800
p-6
rounded-xl
mt-8
">


<h2 className="
text-white
text-xl
mb-4
">

Select Stock

</h2>


<select

className="
w-full
p-3
rounded-lg
bg-slate-700
text-white
"

onChange={(e)=>{

const stock =
stocks.find(
(s)=>s.symbol===e.target.value
);

setSelected(stock);

}}

>


{
stocks.map(stock=>(

<option
key={stock.symbol}
value={stock.symbol}
>

{stock.name}

</option>

))
}


</select>



<div className="
mt-5
text-white
">


<p>
Symbol: {selected.symbol}
</p>


<p>
Sector: {selected.sector}
</p>


<p>
Market: {selected.market}
</p>


</div>



</div>

)

}


export default StockSelector;