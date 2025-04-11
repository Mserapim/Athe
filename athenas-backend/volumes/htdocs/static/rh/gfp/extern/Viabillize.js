Ext.ns('rh.gfp.extern');

rh.gfp.extern.Viabillize = Ext.extend(
    toolkit.widget.TabPanel,
    {

        getTpl: function() {

            if(!this._tpl){
                this._tpl = new Ext.XTemplate(
                    '<div style="border:none; margin:30px auto; display:table">'+
                        '<p style="font-size: 20px;"><b>Passos para realizar uma consignação:</b></p>'+
                        '<ol style="text-align:justify">'+
                        '<li style="width: 400px; margin-bottom:7px; font-size: small;">Acessar o link abaixo para entrar no sistema de consignação, mas leia as instruções abaixo;</li>'+
                        '<li style="width: 400px; margin-bottom:7px; font-size: small;">Verificar sua margem, em caso de dúvida ligue no RH (3216-7565);</li>'+
                        '<li style="width: 400px; margin-bottom:7px; font-size: small;">Clicar no botão "<b>EMITIR NOVA AIC</b>" no canto inferior direito - <b>AIC</b> é o documento exigido pelos consignatários para efetuação da consignação;</li>'+
                        '<li style="width: 400px; margin-bottom:7px; font-size: small;">Imprima a <b>AIC</b> gerada e leve ao consignatário (banco, etc);</li>'+
                        '<li style="width: 400px; margin-bottom:7px; font-size: small;">No banco será validada a <b>AIC</b> recebida e caso confirme sua autenticidade será gerado uma <b>ADF</b> após negociação dos valores, que deverá ser lida e assinada pelo servidor - <b>ADF</b> é a Autorização de Desconto em Folha;</li>'+
                        '<li style="width: 400px; margin-bottom:7px; font-size: small;">Após seguir os passos acima sua consignação estará concluída.</li>'+
                        '</ol>'+
                        '<a style="text-decoration: none; color:#2779aa" href="https://www.viabillize.com.br/MPTO/Serv.aspx?mt={matricula}&pw={pw}&Op=Hist" target="_blank"> Clique aqui para acesso ao Sistema de Consignação </a>'+
                    '</div>'
                );
            }
            return this._tpl;
        },

        getDisplayPanel: function(mat, pw) {
            if(!this._displayPanel) {
                this._displayPanel = new Ext.Panel({
                    'region': 'center',
                    'tpl': this.getTpl(),
                    'data': {matricula: mat, pw: pw},
                    // 'height': 150,
                    // 'minHeight': 150,
                    // 'maxHeight': 150,
                    // 'split': true,
                    // 'forceLayout': true,
                    'preventBodyReset': true,
                    // 'bodyStyle': 'border-left:none;border-bottom:none;border-right:none',
                    // 'autoScroll': true
                });
            }

            return this._displayPanel;
        },

        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});

            Ext.applyIf(cfg, {
                'title': 'Sistema de Consignações',
                'layout': 'border',
                'autoScroll': false,
                'items':[this.getDisplayPanel(cfg.matricula, cfg.pw)]
            });

            rh.gfp.extern.Viabillize.superclass.constructor.call(this, cfg);

            // var ts = toolkit.Application.tabspace;

            // ts.remove(ts.getActiveTab());
            // ts.add(this);
            // ts.setActiveTab(this);
        }
    }
);


function viabillize(matricula, pw){
    try{
        console.debug(matricula);
        console.debug(pw);
        return {
            show: function(){
                var http_ = "http://www.viabillize.com.br/MPTO/Serv.aspx?mt="+matricula+"&pw="+pw+"&Op=Hist";
                console.debug(http_);
                open(http_,"_blank");
            }
        }
    }catch(e){
        console.error(e);
    }
    //http://www.viabillize.com.br/MPTO/Serv.aspx?mt=@MatriculaSemDigitoVerificador&pw=XAHUMPPTO3930A255483FXBNK&Op=Hist&pw=[hash]
}