Ext._define('common.payments.SecondTicketWayForm', {
    extend: 'toolkit.widget.TabPanel',

    getValueTicketNumber: function() {
        if (!this._ticket_number) {
            this._ticket_number = Ext._create('Ext.form.TextField', {
                anchor: '100%',
                fieldLabel: 'Número do Boleto',
                name: 'ticket_number',
                allowBlank: false,
            });
        }
        return this._ticket_number;
    },

    sendForm: function(url,name,keys,values) {

        var newWindow = window.open(url, name);

        if (!newWindow) return false;

        var html = "";
        html += "<html><head></head><body><form id='formid' method='post' action='" + url +"'>";

        if (keys && values && (keys.length == values.length))
            for (var i=0; i < keys.length; i++){
                valor = keys[i] == 'dtVenc' ? values[i].split(' ', 1)[0].replace(/\//g,''):values[i]
                html += "<input type='hidden' name='" + keys[i] + "' value='" + valor + "'/>";
            }

        html += "</form><script type='text/javascript'>document.getElementById(\"formid\").submit()</sc"+"ript></body></html>";
        newWindow.document.write(html);
        return newWindow;
    },

    saveForm: function(fp) {
        var values = this.getFormPanel().getForm().getValues();

        if(fp.getForm().isValid()){
            fp.getForm().submit({
                scope: this,
                url: core.callAction('InternalTicketPayController','ticket_recovery'),
                waitMsg: 'Gerando Boleto ...',

                success: function(form, action)
                {
                    var result = action.result;
                    console.log("RESUlTADO")
                    console.log(result)
                    var keys = new Array(
                        "nome",
                        "indicadorPessoa",
                        "cpfCnpj",
                        "msgLoja",
                        "cep",
                        "cidade",
                        "uf",
                        "endereco",
                        "dtVenc",
                        "tpDuplicata",
                        "tpPagamento",
                        "idConv",
                        "refTran",
                        "urlRetorno",
                        "valor"
                    );

                    var values = new Array(
                       result.obj.nome,
                       result.obj.indicadorPessoa,
                       result.obj.cpfCnpj,
                       result.obj.msgLoja,
                       result.obj.cep,
                       result.obj.cidade,
                       result.obj.uf,
                       result.obj.endereco,
                       result.obj.dtVenc,
                       result.obj.tpDuplicata,
                       result.obj.tpPagamento,
                       result.obj.idConv,
                       result.obj.refTran,
                       result.obj.urlRetorno,
                       result.obj.valor
                    );

                    this.sendForm("https://mpag.bb.com.br/site/mpag/",'pagamento', keys, values)
                },
                failure: function(form, action){
                    if (action.failureType === Ext.form.Action.CONNECT_FAILURE) {
                        Ext.Msg.alert('Error',
                            'Status:'+action.response.status+': '+
                            action.response.statusText);
                    }
                    if (action.failureType === Ext.form.Action.SERVER_INVALID){
                        // server responded with success = false
                        Ext.Msg.alert('Invalid', action.result.errormsg);
                    }
                }
            });
        }
    },

     getFormPanel: function(cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                items: [this.getValueTicketNumber()],
                buttons: [
                    {
                        text: 'Emitir',
                        formBind: true,
                        scope: this,
                        handler: function() {
                            this.saveForm(this._formPanel);
                        }
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(
            cfg,
            {
               title: 'Segunda Via de Boleto'
            }
        );

        Ext.apply(
            cfg,
            {
                items:[
                    {
                        xtype: 'container',
                        autoEl: 'div',
                        width: 500,
                        style: {
                            padding: '50px',
                            margin: '0 auto'
                        },
                        items: {
                            title: 'Emitir segunda via de Boleto',
                            items: [
                                this.getFormPanel(cfg)
                            ]
                        }
                    }
                ]
            }
        );

       common.payments.SecondTicketWayForm.superclass.constructor.call(this, cfg);
    }
});
