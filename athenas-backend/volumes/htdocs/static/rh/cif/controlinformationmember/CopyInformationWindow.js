

Ext._define('cif.controlinformationmember.CopyInformationWindow', {
    extend: 'Ext.Window',

    getCurrentYear: function(){
        var mydate= new Date()
        year = mydate.getFullYear();
        return year
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "rest-autocompletefield", 
                        width: 250,
                        fieldLabel: "Período de Referência Anterior", 
                        allowBlank: true, 
                        rest: "cif.referenceperiod.ReferencePeriodRestful", 
                        name: "previous_referenceperiod"
                    }, 
                    {
                        xtype: "textfield",
                        width: 250, 
                        fieldLabel: "Per\u00edodo de Exer\u00edcio", 
                        allowBlank: false, 
                        allowDecimals: false, 
                        name: "exercise",
                        emptyText: 'Insira no formato: Ano/Periodo ex: '+ this.getCurrentYear() +'/01'
                    },
                    {
                        allowBlank: true, 
                        width: 250,
                        fieldLabel: "Data In\u00edcio Exer\u00edcio", 
                        name: "start_date", 
                        xtype: "datefield"
                    }, 
                    {
                        allowBlank: true, 
                        width: 250,
                        fieldLabel: "Data Fim Exer\u00edcio", 
                        name: "end_date", 
                        xtype: "datefield"
                    }, 
                ]
                    
            });
        return this._formPanel;
    },

    save: function(){
        var form = this.getFormPanel().getForm();

        var rest = Ext._create('cif.controlinformationmember.ControlInformationMemberRestful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('copy_referenceperiod', false, 'POST', {
                scope: this,
                params: {
                    previous_referenceperiod: form.getValues().previous_referenceperiod,
                    exercise: form.getValues().exercise,
                    start_date: form.getValues().start_date,
                    end_date: form.getValues().end_date,
                },
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                        this.destroy();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Atenção',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponível no momento.'
                    });
                },
            })
        );
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
        	cfg,
        	{
        		title: 'Copiar Períodos de Referência',
        		closable: true,
				height: 230,
        		width: 400
        	}
        );
		Ext.apply(
			cfg,
			{
				border: false,
				layout: 'fit',
				items: [
					this.getFormPanel(cfg)
				],
                buttons: [
                    {
                        text: 'Enviar',
                        scope: this,
                        handler: this.save
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]   
			}
		);
		cif.controlinformationmember.CopyInformationWindow.superclass.constructor.call(this, cfg);
    }
});