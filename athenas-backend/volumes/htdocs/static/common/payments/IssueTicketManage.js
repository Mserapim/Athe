Ext._define('common.payments.IssueTicketManage', {
    extend: 'toolkit.widget.TabPanel',


    getValueName: function(v) {
        if (!this._name) {
            this._name = Ext._create('Ext.form.DisplayField', {
                anchor: '100%',
                // fieldLabel: 'Nome',
                name: 'nome',
                value: v,
                // hidden: true,
                allowBlank: false,
            });
        }
        return this._name;
    },

    getValueCPF: function(v) {
        if (!this._cpf) {
            this._cpf = Ext._create('Ext.form.DisplayField', {
                anchor: '100%',
                //fieldLabel: 'CPF',
                name: 'cpfCnpj',
                value: v,
                //hidden: true,
                allowBlank: false,
            });
        }
        return this._cpf;
    },

    getValueName: function(v) {
        if (!this._name) {
            this._name = Ext._create('Ext.form.TextField', {
                anchor: '100%',
                fieldLabel: 'Nome',
                name: 'nome',
                value: v,
                hidden: true,
                allowBlank: false,
            });
        }
        return this._name;
    },

    getValueCPF: function(v) {
        if (!this._cpf) {
            this._cpf = Ext._create('Ext.form.TextField', {
                anchor: '100%',
                fieldLabel: 'CPF',
                name: 'cpfCnpj',
                value: v,
                hidden: true,
                allowBlank: false,
            });
        }
        return this._cpf;
    },

    getValueCEP: function(v) {
        if (!this._cep) {
            this._cep = Ext._create('Ext.form.TextField', {
                anchor: '100%',
                fieldLabel: 'CEP',
                name: 'cep',
                value: v,
                hidden: true,
                allowBlank: false,
            });
        }
        return this._cep;
    },

    getValueCity: function(v) {
        if (!this._city) {
            this._city = Ext._create('Ext.form.TextField', {
                anchor: '100%',
                fieldLabel: 'Cidade',
                name: 'cidade',
                value: v,
                hidden: true,
                allowBlank: false,
            });
        }
        return this._city;
    },

    getValueUF: function(v) {
        if (!this._uf) {
            this._uf = Ext._create('Ext.form.TextField', {
                anchor: '100%',
                fieldLabel: 'UF',
                name: 'uf',
                value: v,
                hidden: true,
                allowBlank: false,
            });
        }
        return this._uf;
    },

    getValueAddress: function(v) {
        if (!this._address) {
            this._address = Ext._create('Ext.form.TextField', {
                anchor: '100%',
                fieldLabel: 'Endereço',
                name: 'endereco',
                value: v,
                hidden: true,
                allowBlank: false,
            });
        }
        return this._address;
    },

    getValueMoney: function() {
        if (!this._money) {
            this._money = Ext._create('Ext.form.NumberField', {
                anchor: '40%',
                fieldLabel: 'Valor',
                name: 'valor',
                allowBlank: false,
                maxLength: 16,  // 15 digits + 1 seperator
                decimalSeparator: ',',
            });
        }
        return this._money;
    },

     getValueMessage: function() {
        if (!this._message) {
            this._message = Ext._create('Ext.form.TextArea', {
                anchor: '100%',
                fieldLabel: 'Justificativa',
                name: 'msgLoja',
                allowBlank: false
            });
        }
        return this._message;
    },

    getValueIdentifier: function() {
        if (!this._identifier) {
            this._identifier = Ext._create('Ext.form.TextField', {
                name: 'identifier',
                value: 'INTERNAL_PAYMENT',
                hidden: true,
                submitValue: true,
            });
        }
        return this._identifier;
    },

    getValuePersonType: function(v) {
        if (!this._person_type) {
            this._person_type = Ext._create('Ext.form.TextField', {
                name: 'person_type',
                value: v,
                hidden: true,
                submitValue: true
            });
        }
        return this._person_type;
    },

    getValueProcess: function() {
        if (!this._process_number) {
            this._process_number = Ext._create('Ext.form.TextField', {
                name: 'process_number',
                value: '00000000000000000000',
                hidden: true,
                submitValue: true
            });
        }
        return this._process_number;
    },

    getValueSituation: function() {

        if(!this._situation)
            this._situation = new Ext.form.ComboBox({
                emptyText: 'Selecione o Motivo da Despesa',
                fieldLabel: 'Despesa',
                anchor: '99%',
                hiddenName: 'motivo',
                name: 'motivo',
                store: [
                    [ 'Devolução de Diárias', 'Devolução de Diárias'],
                    [ 'Devolução de subsídios e Vencimentos', 'Devolução de subsídios e Vencimentos'],
                    [ 'Outros Ressarcimentos/Devoluções ao Erário', 'Outros Ressarcimentos/Devoluções ao Erário']
                ]
            });

        return this._situation;
    },

    resetForm: function(fp) {
        fp.getForm().reset();
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
        if (fp.getForm().isValid()) {
            fp.getForm().submit({
                scope: this,
                url: core.callAction('InternalTicketPayController','ticket_save'),
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
                        //,
                        Ext.Msg.alert('Invalid', action.result.error);
                    }
                }
            });
        }
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                scope: this,
                items: [
                    this.getValueIdentifier(),
                    this.getValuePersonType(cfg.employee_person_type),
                    this.getValueName(cfg.employee_name),
                    this.getValueCPF(cfg.employee_cpf),
                    this.getValueCEP(cfg.employee_cep),
                    this.getValueCity(cfg.employee_city),
                    this.getValueUF(cfg.employee_state),
                    this.getValueAddress(cfg.employee_address),
                    this.getValueProcess(),
                    this.getValueSituation(),
                    this.getValueMessage(),
                    this.getValueMoney(),
                ],
                buttons: [
                    {
                        text: 'Limpar',
                        scope: this,
                        handler: function() {
                            this.resetForm(this._formPanel);
                        }
                    },
                    {
                        text: 'Salvar',
                        formBind: true,
                        scope: this,
                        handler: function() {
                            this.saveForm(this._formPanel);
                        }
                    }
                ]
            });
        }
        return this._formPanel;
    },

    getTicketCmp: function(cfg) {
        var cmp = {};
        if(cfg.success)
        {
            cmp = {
                title: 'Dados do Boleto',
                items: [
                    this.getFormPanel(cfg.data)
                ]
            }
        }
        else
            Ext.Msg.alert('Erro', cfg.message);

        return cmp;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(
            cfg,
            {
               title: 'Formulário de Boleto'
            }
        );

        Ext.apply(
            cfg,
            {
                items:[
                    {
                        xtype: 'container',
                        autoEl: 'div',
                        width: 700,
                        style: {
                            padding: '50px',
                            margin: '0 auto',
                        },
                        items: this.getTicketCmp(cfg)
                    }
                ]
            }
        );

       common.payments.IssueTicketManage.superclass.constructor.call(this, cfg);
    }
});
