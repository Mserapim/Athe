rh.employee.specialized.tab.fields.Functional = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function (cfg) {
            rh.employee.specialized.tab.fields.Functional.superclass.constructor.call(this, cfg);
            this.setOrganIdentifier(cfg.organIdentifier);
            this.setMatriculaFieldBlocked(cfg.matriculaFieldBlocked);
        },

        setOrganIdentifier: function (organIdentifier) {
            this.organIdentifier = organIdentifier;
        },

        setMatriculaFieldBlocked: function (matriculaFieldBlocked) {
            this.matriculaFieldBlocked = matriculaFieldBlocked;
        },

        getOrganIdentifier: function () {
            return this.organIdentifier;
        },

        getMatriculaFieldBlocked: function () {
            return this.matriculaFieldBlocked;
        },

        fields: function () {
            var column1_items = [];
            var column2_items = [];
            column1_items.push(
                this.getTypeByPossessionChoiceField(),
            );
            column1_items.push(
                this.getMatriculaTextField(),
            );
            column1_items.push({
                width: '90%',
                name: 'data_referencia_ferias',
                fieldLabel: 'Data referência férias',
                xtype: 'datefield',
                allowBlank: true,
            });
            column1_items.push(
                this.getDegreeEducationChoiceField({ value: 8 })
            );
            column1_items.push({
                width: '70%',
                xtype: 'rest-autocompletefield',
                fieldLabel: 'Chefe imediato',
                name: 'chefe_imediato',
                displayField: 'unicode',
                allowBlank: true,
                rest: 'rh.employee.Restful'
            });
            column2_items.push({
                width: '80%',
                name: 'matricula_origem',
                fieldLabel: 'Matrícula de Origem',
                xtype: 'textfield',
                allowBlank: true,
            });
            column2_items.push({
                width: '80%',
                name: 'numero_cartao_ponto',
                fieldLabel: 'N° Cartão de Ponto',
                xtype: 'numberfield',
                allowBlank: true,
            });
            // column2_items.push({
            //     width: '60%',
            //     name: 'founder_employee',
            //     fieldLabel: 'Instituidor do benefício',
            //     xtype: 'rest-autocompletefield',
            //     allowBlank: true,
            //     rest: 'rh.employee.Restful'
            // });

            var c = new Ext.Panel({
                region: 'north',
                height: 200,
                width: 1200,
                layout: 'form',
                items:[
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: column1_items
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: column2_items
                            }
                        ]
                    },
                    this.getDegreeEducationChoiceField({value: 8}),
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.7',
                                layout: 'form',
                                items: [{
                                    fieldLabel: "Categoria (eSocial)",
                                    name: "category_esocial",
                                    xtype: "choicefield",
                                    hiddenName: "category_esocial",
                                    choiceId: "rh.CATEGORY_WORKER",
                                    width: 692,
                                }]
                            },
                            {
                                columnWidth: '0.3',
                                layout: 'form',
                                items: [{
                                    fieldLabel: "Posição no Concurso",
                                    name: "posicao_concurso",
                                    xtype: "numberfield",
                                    width: 160,
                                    allowBlank: true,
                                }]
                            }
                        ]
                    }
                ]
            });

            var column = [c];
            return column;
        },

        getDegreeEducationChoiceField: function (cfg) {
            if (!this._degreeEducationChoiceField) {
                cfg = cfg || {};
                Ext.applyIf(cfg, {
                    fieldLabel: 'Grau Instrução',
                    hiddenName: 'grau_instrucao',
                    choiceId: 'rh.DEGREE_EDUCATION',
                    width: 450,
                });
                this._degreeEducationChoiceField = Ext._create('standard.fields.ChoiceField', cfg);
                var store = this._degreeEducationChoiceField.getStore();
                var filter = Ext.decode(store.baseParams.filter);
                filter.push({ property: 'value__in', value: [3, 12, 13, 14], stage: -1 });
                store.baseParams.filter = Ext.encode(filter);
                store.load();
            }
            return this._degreeEducationChoiceField;
        },

        getTypeByPossessionChoiceField: function () {
            if (!this.typeByPossessionChoiceField) {
                this.typeByPossessionChoiceField = Ext._create('standard.fields.ChoiceField', {
                    width: 450,
                    hiddenName: 'type_by_possession',
                    fieldLabel: 'Tipo de Servidor',
                    choiceId: 'rh.CLASSIF_EMPLOYEE_BY_POSSESSION',
                    valueField: 'cvalue',
                });
                if (this.getOrganIdentifier() === 'mpmt') {
                    var store = this.typeByPossessionChoiceField.getStore();
                    var filter = Ext.decode(store.baseParams.filter);
                    filter.push({ property: 'value__in', value: [1, 3, 7, 8, 10, 11, 12, 14, 15, 16, 17, 20, 28, 31], stage: 1 });
                    store.baseParams.filter = Ext.encode(filter);
                    store.load();
                }
            }
            return this.typeByPossessionChoiceField;
        },

        getMatriculaTextField: function () {
            if (!this.matriculaTextField) {
                var field_params = {
                    width: 450,
                    name: 'matricula',
                    fieldLabel: 'Matrícula',
                    allowBlank: true,
                    style: "background: #E5E5E5; color:#686767"
                    // validateOnBlur: true,
                    // blankText: 'É necessário preencher o campo Matrícula.',
                }
                if (this.getMatriculaFieldBlocked() === 'true') {
                    field_params['disabled'] = true;
                    field_params['readOnly'] = true;
                }

                this.matriculaTextField = Ext._create('Ext.form.TextField', field_params);
            }
            return this.matriculaTextField;
        },
    }
);

