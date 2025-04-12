/**
 *
 **/
Ext._define('rh.pesquisa.EscolaridadeAvisoWindow', {
    'extend': 'Ext.Window',

    getText: function(){
        text =  '<p><strong><font color="#FFFF00" size="4"> ATENÇÃO </font></br></strong></p>'+
        '<p align="left"> Sr(a). Servidor(a), </br> Para fins de atualização dos seus assentamentos funcionais, solicitamos preencher os dados na tela seguinte, observando:</br>'+
        '<strong>1)</strong> Prazo para preenchimento das informações: até 27 de setembro de 2013;<br>'+
        '<strong>2)</strong> Inclua todos os níveis de escolaridade/graduações/títulos adquiridos, e que possam ser devidamente comprovados;</br>'+
        '<strong>3)</strong> Passos para inclusão das informações: Na tela seguinte clique no botão <b><i><font color="#FFFF00">Novo=>Preencha os dados=>Salve o formulário;</b></i></font></br>'+
        'ou no menu <b><i><font color="#FFFF00">PORTAL DO SERVIDOR=>Censo de Escolaridade=>Novo=>Preencha os dados=>Salve o formulário;</b></i></font></br>'+
        '<strong>4)</strong> Oportunamente será exigida a apresentação da documentação objeto das referidas inclusões. </p>'+
        '<p><strong> Dúvidas ligue para: 3216-7565 - 7692 - 7650 </br> DRHFP </strong><p>'
        return text
    },

    getFooterText: function(){
        text  = '<p align="left"><font color="FFFF00">Feche esta janela para ir à "tela seguinte".</font></p>';
        return text
    },

    getTemplate: function(){
       return {
            region:'center',
            height:100,
            html: new Ext.Template(
                '<div class="warnings">',
                    this.getText(),
                    this.getFooterText(),
                '</div>'
            ).apply()

        } 
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                'title': 'Pesquisa de Escolaridade',
            }
        );
        var box = Ext.getBody().getBox();
        Ext.apply(
            cfg,
            {
                items: this.getTemplate(),
                layout: 'border',
                border: true,
                width: 800,
                height: 300,
                modal:true,
            }
        );
        // this.callParent([cfg]);
        rh.pesquisa.EscolaridadeAvisoWindow.superclass.constructor.call(this, cfg);
    }
});