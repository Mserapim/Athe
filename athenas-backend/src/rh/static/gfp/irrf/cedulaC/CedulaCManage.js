Ext._define('rh.gfp.irrf.cedulaC.CedulaCManage', {
	extend: 'Ext.Window',

    getFormPanel: function (cfg) {
        if (this._formPanel) {
            return this._formPanel;
        }

        this._formPanel = Ext._create('Ext.form.FormPanel', {
            border: false,
            frame: true,
            labelWidth: 95,
            items: [
                this.getFileField(cfg),
                this.getYearField(cfg),
                this.getTypeField(cfg),   
                this.getRetificationField(cfg),
            ]
        });

        return this._formPanel;
    },

    _getValues: function () {
        this.validateFields();
        var values = this.getFormPanel().getForm().getValues();
        return values
    },

    validateFields: function () {
        if (this.getFormPanel().getForm().isValid() && 
            this.getFileField().getValue() != '' &&
            this.getYearField().getValue() != '' &&
            this.getTypeField().getValue()
            ) { 
            return;
        }

        var msg = 'Um ou mais campos não foram preenchidos corretamente.';
        Ext.Msg.show({
            title: 'Erro',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK,
            msg: msg,
        });
        throw msg;
    },

    getFileField: function (cfg) {
        if (this._fileUploadField) {
            this._fileUploadField;
        }

        this._fileUploadField = Ext._create('core.fields.FileUploadField', {
            fieldLabel: 'Arquivo',
            allowBlank: false,
            name: 'file',
            loadingOwner: this,
            width: 480,
            access: core.fields.FileUploadField.ACCESS.PUBLIC,
        });

        return this._fileUploadField;
    },

    getYearField: function(cfg) {
        if (!this._yearField)
            this._yearField = Ext._create('Ext.form.ComboBox', {
                name: 'year',
                fieldLabel: 'Ano de Referência',
                triggerAction: 'all',
                editable: false,
                store: this.getYearStore(),
                anchor: '90%',
                allowBlank: true
            });
        return this._yearField;
    },

    getTypeField: function(cfg) {
        if (!this._typeField)
            this._typeField = Ext._create('Ext.form.ComboBox', {
                name: 'type',
                fieldLabel: 'Órgão Emissor',
                triggerAction: 'all',
                editable: false,
                store: [
                    ['MPMT', 'MPMT'],
                    ['TRE', 'TRE']
                ],
                anchor: '90%',
                allowBlank: true
            });
        return this._typeField;
    },

    getRetificationField: function (cfg) {
        if (!this._urgencyField) {
            this._urgencyField = Ext._create('Ext.form.Checkbox', {
                name: 'retification',
                hideLabel: true,
                boxLabel: 'Retificação'
            });
        }

        return this._urgencyField;
    },


    /**
    * Metodo que retrona um Array contendo anos, partindo-se de uma data default (2023)
    * até o ano atual
    * @param initialYear: Integer opcional para subsbtituir a data inicial default
    */
    getYearStore: function(initialYear) {
        initialYear = initialYear || 2023;
        var currentYear = (new Date()).getFullYear();
        var store = [];
        for (var year = currentYear; year >= initialYear; year--)
            store.push([year, year.toString()]);
        return store;
    },
  
    /**
    * Metodo que faz chamada Ajax para importar Cédula C, encaminhando o arquivo e o ano de referência da Cédula-c
    * para que o arquivo seja divido e serparado por servidor.
    * 
    * @param values: Array contendo os valores a serem enviados como parâmentro
    */
	importCedulaC: function(values) {
		Ext.Ajax.request({
			url: toolkit.util.Normalize.controller_action('CedulaCIRPF', 'import_cedula_c'),
			params: JSON.parse(JSON.stringify(values)),
			method: 'POST',
			scope: this,
			success: function(request) {
				var obj = Ext.decode(request.responseText);

				if(!obj.success)
					Ext.Msg.show({
						title: this.title,
						icon: Ext.Msg.ERROR,
						buttons: Ext.Msg.OK,
						msg: obj.message
					});
			},
			failure: function(request) {
				Ext.Msg.show({
					title: this.title,
					icon: Ext.Msg.ERROR,
					buttons: Ext.Msg.OK,
					msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
				});
			}
		});
	},

    /**
    * Metodo que chama um modal de confirmação para importação da cédula-c
    * 
    * @param values: Array contendo os valores a serem enviados como parâmentro
    */
	_confirmation: function(values){
		Ext.Msg.show({
			title: 'Importar Cédula C',
			msg: 'Tem certeza que deseja importar a Cédula C?',
			icon: Ext.Msg.QUESTION,
			buttons: Ext.Msg.YESNO,
			scope: this,
			fn: function(btn) {
				if(btn == 'no') return this.destroy();

				this.importCedulaC(values);
			}
		});
	},

	// Buttons
    _getAddButton: function (cfg) {
        if (this._addButton) {
            return this._addButton;
        }
        this._addButton = Ext._create('Ext.Button', {
            text: 'Importar Cédula C',
            scope: this,
            handler: function () {
                values = this._getValues()
                this.validateFields();
                this._confirmation( values);
                this.destroy();
            },
        });

        return this._addButton;
    },

    _getCloseButton: function (cfg) {
        if (this._closeButton) {
            return this._closeButton;
        }

        this._closeButton = Ext._create('Ext.Button', {
            text: 'Fechar',
            scope: this,
            handler: function () {
                this.destroy();
            },
        });

        return this._closeButton;
    },

    _getButtons: function (cfg) {
        if (this._buttons) {
            return this._buttons;
        }

        this._buttons = [];
        this._buttons.push(this._getAddButton(cfg));
        this._buttons.push(this._getCloseButton(cfg));

        return this._buttons;
    },

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Importador de Cédula C',
			   operation: 'create',
			}
		);


        Ext.apply(cfg, {
            modal: true,
			resizable: false,
			border: false,
			width: 600,
            items: [ this.getFormPanel(cfg), ],
            buttons: this._getButtons(cfg),
        });

		rh.gfp.irrf.cedulaC.CedulaCManage.superclass.constructor.call(this, cfg);
	}
});
