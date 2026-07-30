function ModelComparison(){

const models=[

{
name:"LSTM",
rmse:"0.032",
mae:"0.021",
accuracy:"91.5%"
},

{
name:"CNN/LSTM",
rmse:"0.041",
mae:"0.030",
accuracy:"89.7%"
},

{
name:"Transfer Learning",
rmse:"0.025",
mae:"0.018",
accuracy:"93.2%"
}

];


return (

<div className="
bg-slate-800
rounded-xl
p-6
mt-10
text-white
">


<h2 className="
text-xl
font-bold
mb-5
">

Model Performance Comparison

</h2>


<table className="w-full table-auto">

    <thead>

        <tr className="border-b border-slate-700">

            <th className="text-left py-3 px-4">Model</th>
            <th className="text-left py-3 px-4">RMSE</th>
            <th className="text-left py-3 px-4">MAE</th>
            <th className="text-left py-3 px-4">Accuracy</th>

        </tr>

    </thead>

    <tbody>

        {models.map((model) => (

            <tr
                key={model.name}
                className="border-b border-slate-700 hover:bg-slate-700"
            >

                <td className="py-4 px-4">{model.name}</td>
                <td className="py-4 px-4">{model.rmse}</td>
                <td className="py-4 px-4">{model.mae}</td>
                <td className="py-4 px-4 text-green-400">{model.accuracy}</td>

            </tr>

        ))}

    </tbody>

</table>


</div>

)

}


export default ModelComparison;