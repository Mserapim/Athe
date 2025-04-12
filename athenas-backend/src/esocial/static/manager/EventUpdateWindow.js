Ext._define('esocial.manager.EvenUpdateWindow', {
	extend: 'Ext.Window',

	width: 500,

	getFormPanel: function (cfg) {
		if (!this.formPanel)
			this.formPanel = new Ext.form.FormPanel({
				border: false,
                frame: true,
				items: [
                    this.getProcessStatusField(),
                    this.getEventField()
                ],
			});

        return this.formPanel;
    },

    getProcessStatusField: function (cfg) {
        if(!this._processStatusField)
            this._processStatusField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Status processamento (evento)',
                hiddenName: 'process_status',
                choiceId: 'esocial.STATUS_EVENT',
                name: 'process_status',
                width: 350,
            });
        return this._processStatusField;
    },

    getEventField: function (cfg) {
        if(!this._eventField)
            this._eventField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Evento',
                allowBlank: false,
                readOnly: true,
                hidden: true,
                rest: 'esocial.manager.EventRestful',
                name: 'event'
            });
        return this._eventField;
    },

	executeAction: function (action, params, msg) {
		var rest = Ext._create('esocial.manager.EventRestful', {});
		var mask = new Ext.LoadMask(this.getEl(), { msg: msg ? msg : 'Aguarde...' });
		var wnd = this;

		mask.show();
		rest.executeAction(
			action,
			params,
			{
				scope: this,
				fn: function (rst) {
					core.invokeCallback((wnd.externalCallback || { fn: Ext.emptyFn }), rst, wnd);
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

	constructor: function (cfg) {
		cfg = core.nullValue(cfg, {});

		Ext.applyIf(cfg, {
			title: 'Editar Evento'
		});

		Ext.apply(cfg, {
			border: false,
			items: [
				this.getFormPanel()
			],
			buttons: [{
				text: 'Salvar',
				scope: this,
				handler: function(){
					var values = this.getFormPanel().getForm().getValues();
					this.executeAction('update_process_status', values, 'Atualizando evento...');
                    this.close();
				}
			},
			{
				text: 'Cancelar',
				scope: this,
				handler: function () { this.close(); }
			}
			]
		});

		esocial.manager.EvenUpdateWindow.superclass.constructor.call(this, cfg);

        this.getProcessStatusField().setValue(cfg.process_status);
        this.getEventField().setValue(cfg.event);
	},

});
