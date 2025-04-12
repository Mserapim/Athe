Ext._define('edocs.protocolo.requestform.mixins.Common', {

    // O método a seguir tenta setar o valor padrão pelo nome do
    // tipo de documento, ao invés de usar o pk diretamente, que
    // é uma má pratica.
    getDocumentTypeField: function (name) {
        if (!this._tipoDocumentoField) {
            this._tipoDocumentoField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Tipo',
                name: 'document_type',
                resizable: true,
                rest: 'edocs.protocolo.TipoDocumentoRestful',
                width: 210,
                allowBlank: false,
            });

            this._tipoDocumentoField.setReadOnly(true);

            if (typeof name === 'string') {
                // Aqui é configurada uma query muito específica
                // que, em tese, trará apenas um registro.
                this._tipoDocumentoField.setPreFilter([
                    { property: 'habilita', value: 'on', stage: 1001 },
                    { property: 'nome', value: name, stage: 1002 }
                ]);

                // Se o store for carregado com êxito, com base na query
                // especificada, setamos um valor padrão para o campo
                // somente-leitura. Senão, habilitamos o campo e deixamos
                // o usuário escolher.
                var canPickUpTheFirst = true;
                this._tipoDocumentoField.getComboField().getStore().on(
                    'load',
                    function (records) {
                        if (records.getAt(0) && canPickUpTheFirst) {
                            this._tipoDocumentoField.setValue(records.getAt(0).data.pk);
                        } else {
                            canPickUpTheFirst = false;
                            this._tipoDocumentoField.setPreFilter([
                                { property: 'habilita', value: 'on', stage: 1001 }
                            ]);
                            this._tipoDocumentoField.setReadOnly(false);
                        }
                    },
                    this
                );

                this._tipoDocumentoField.getComboField().getStore().load();
            } else {
                this._tipoDocumentoField.setPreFilter([
                    { property: 'habilita', value: 'on', stage: 1001 }
                ]);
                this._tipoDocumentoField.setReadOnly(false);
            }
        }

        return this._tipoDocumentoField;
    },

    getContactNumberField: function (cfg, config) {
        if (!this._contactNumberField) {
            this._contactNumberField = Ext._create('core.fields.PhoneField', {
                fieldLabel: 'Telefone',
                name: 'contact_number',
                width: (config || {}).width || '25%',
                allowBlank: true
            });
        }

        return this._contactNumberField;
    },

    getChoiceFieldSet: function (config) {
        if (this._requestTypeField) {
            return this._requestTypeField;
        }

        function required (argumentName) {
            throw new Error(`ChoiceFieldSet: '${argumentName}' is required`);
        }

        Ext.applyIf(config, {
            title: 'ChoiceFieldSet',
            choiceId: null,
            name: null,
            value: null,
            columns: 1,
        });

        config.choiceId || required('choiceId');
        config.name || required('name');

        this._requestTypeField = Ext._create('Ext.form.FieldSet', {
            title: config.title,
        });

        var choices = Ext._create('standard.ChoiceActiveRestful').getStore();

        choices.setBaseParam('filter', Ext.encode([{
            property: 'cache_path',
            value: config.choiceId,
        }]));

        choices.load({
            scope: this,
            add: false,
            callback: function (records, options, success) {
                var radios = records.map(function(record) {
                    return {
                        xtype: 'radio',
                        boxLabel: record.data['label'],
                        name: config.name,
                        inputValue: record.data['value'],
                        hideLabel: true,
                        checked: config.value === record.data['value'],
                    };
                }, this);

                this._requestTypeField.insert(0, {
                    xtype: 'radiogroup',
                    columns: config.columns,
                    name: config.name,
                    hideLabel: true,
                    items: radios,
                });

                this._requestTypeField.doLayout();
            },
        });

        return this._requestTypeField;
    },
});
