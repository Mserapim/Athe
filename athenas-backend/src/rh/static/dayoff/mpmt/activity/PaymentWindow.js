Ext._define('rh.dayoff.mpmt.activity.PaymentWindow', {
    extend: 'rh.dayoff.mpmt.activity.Window',

    width: 600,

    getStatus(month, year, count){
        const timeElapsed = Date.now();
        const date = new Date(timeElapsed);

        var thisYear = date.getFullYear();
        var thisMonth = date.getMonth() + 1;
        var thisDate = new Date(thisYear, thisMonth)

        var paymentDate = new Date(year, month + count)
        var status = ""

        if (paymentDate < thisDate){
            status = 'Pagos'
        }
        if (paymentDate.getTime() == thisDate.getTime()){
            status = 'Em Processamento'
        }
        if (paymentDate > thisDate){
            status = 'Agendado'
        }
        return status

    },

    setLabelParcel:function(cfg){
        var data = cfg.values.selected.json
        var resultParcel = []
        var parcels = []
        installments = data.payment_installments ? data.payment_installments : 0;

        if (data.parcelas_detalhadas) {
            parcels = data.parcelas_detalhadas
        } else {
            for(var i =1; i < installments+1; i++){
                parcels.push({'parcela': 'Parcela '+i, 'flag': this.getStatus(data.payment_month, data.payment_year, i) })   
            }
        }

        parcels.forEach(function(parcel, i) {
            resultParcel.push( {
                'columnWidth': .9,
                'layout': 'form',
                'items': [
                    {
                        'xtype': 'displayfield',
                        'fieldLabel':parcel.parcela ,
                        'anchor': '99%',
                        'value':parcel.flag,
                    }
                ]
            })
        })
        
        return resultParcel
    },

    setCompentenceLabel: function(cfg){
        var data = cfg.values.selected.json
        if(data.payment_month){
            return data.payment_month + '/' + data.payment_year
        }else{
            return ''
        }
    },

    setInstallmentsLabel: function(cfg){
        var data = cfg.values.selected.json
        return data.payment_installments
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items:[
                    {
                        xtype: 'fieldset',
                        title: 'Pagamento - Usufruto',
                        layout: 'form',
                        style: 'text-align: center !important',
                        items: [
                            {
                                fieldLabel: 'Competência de Pagamento',
                                name: 'competence',
                                value: this.setCompentenceLabel(cfg),
                                xtype: 'textfield'
                            },
                            {
                                fieldLabel: 'Numero de Parcelas',
                                name: 'payment_installments',
                                value: this.setInstallmentsLabel(cfg),
                                xtype: 'numberfield'
                            },
                            {
                                xtype: 'fieldset',
                                hidden:cfg.vdf?true:false,
                                title: 'Parcelas:',
                                layout: 'form',
                                items:this.setLabelParcel(cfg)
                               
                            }
                          
                        ]
                    },
                ]
            });

        return this._formPanel;
    },



    save: function (cfg) {
        var values = this.getFormPanel().getForm().getValues();
        var data = cfg.values.selected.json

        var params = {
            actionCustom: cfg.actionCustom,
            activity: this.oId,
            usufrutct_pk: data.pk,
            competence: values.competence,
            qtd_parcel: values.payment_installments,
        };

        if (this.action == 'update')
            this._update_activity(params);
        else
            this._process(cfg,params);
    },

    getButtons: function (cfg) {
        if (!this._buttons)
            this._buttons = [
                {
                    id: 'btn_save',
                    text: '<b>Salvar</b>',
                    scope: this,
                    handler: function () {
                        this.save(cfg);
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function () {
                        this.close();
                    }
                }
            ];
        return this._buttons;
    },

    _process: function (cfg,params) {
        var rest = Ext._create('rh.dayoff.mpmt.acquisitionperiod.Restful', { resource: this.acquisitionPeriodRestful });
        var mask = Ext._create('Ext.LoadMask', this.getEl(), { msg: 'Processando informações.' });
        var wnd = this;

        params.action = this.action;

        mask.show();
        rest._process(
            params,
            {
                scope: this,
                fn: function (rst) {
                    core.invokeCallback((wnd.externalCallback || { fn: Ext.emptyFn }), rst.message);
                    wnd.close();
                    if (cfg.owner_grid)
                        cfg.owner_grid.getStore().reload()
                    else
                        this.ownerGrid.getStore().reload()
                }
            },
            {
                fn: function (message) {
                    Ext.Msg.show({
                        title: 'Informando',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: message
                    });
                }
            },
            {
                fn: function () {
                    mask.hide();
                }
            }
        );
    },

  
});
