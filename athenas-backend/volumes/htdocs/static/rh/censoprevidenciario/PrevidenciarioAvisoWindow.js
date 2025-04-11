/**
 *
 **/
Ext._define('rh.pesquisa.PrevidenciarioAvisoWindow', {
    'extend': 'Ext.Window',

    getText: function(){
        text =  '<p><strong><font color="#FFFF00" size="4"> Cadastre seu tempo de contribuição à Previdência Social </font></br></strong></p>'+
        '<p align="left"><font color="#FFFF00"> <strong> O quê?</strong></font> Cadastrar todo o período que contribuiu para a previdência social, tanto para Regimes Próprios (RPPS) quanto para o Regime Geral (RGPS);</br>'+
        '<font color="#FFFF00"><strong>Quem?</strong></font> Membros e servidores efetivos do MPE/TO;<br>'+
        '<font color="#FFFF00"><strong>Quando?</strong></font> de 18/10/2013 a 14/11/2013;</br>'+
        '<font color="#FFFF00"><strong>Como e Onde?</strong></font> Acesse <b><i><font color="#FFFF00">Portal do Servidor=>Censo Previdenciário=>Novo=>Preencha os dados=>Salve o formulário;</b></i></font> Cadastre por período: início e fim. Não cadastre o seu tempo de contribuição à previdência referente ao seu vínculo com o MPE/TO, exceto se houve investidura em cargo comissionado, antes de investidura em cargo efetivo no âmbito deste MP.</br>'+
        '<font color="#FFFF00"><strong>Para quê?</strong></font> Os dados servirão de base para atender o sistema de controle de benefícios previdenciários, em fase de desenvolvimento, possibilitando a todos os Integrantes do MPE/TO, calcular o tempo faltante para sua aposentadoria ou outros benefícios vinculados à Previdência Social.</br>'+
        '&nbsp;&nbsp;&nbsp;&nbsp; Não será exigida a apresentação de cópia de certidões de contribuições previdenciárias.</br>'+
        '&nbsp;&nbsp;&nbsp;&nbsp; Vale lembrar que as referidas certidões originais devem permanecer em poder do titular, e só deverão ser entregues ao IGEPREV quando do pedido de algum benefício. Por exemplo, Aposentadoria ou Abono de Permanência.</p></br>'+
        '<p><font color="#FFFF00"><strong> Dúvidas:</font> ligue para: 3216-7565 - 7692 - 7650 </br> DRHFP </strong><p>'
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
                    // this.getFooterText(),
                '</div>'
            ).apply()

        } 
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                'title': 'Censo Previdenciário',
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
                height: 400,
                // autoHeight:true,
                modal:true,
                autoScroll: true,
            }
        );
        // this.callParent([cfg]);
        rh.pesquisa.PrevidenciarioAvisoWindow.superclass.constructor.call(this, cfg);
    }
});