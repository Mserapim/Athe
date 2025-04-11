rh.employee.specialized.tab.fields.AnotherInformation = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function (cfg) {
            rh.employee.specialized.tab.fields.AnotherInformation.superclass.constructor.call(this, cfg);
        },

        observerEmployeePk: function () {
            rh.employee.specialized.tab.fields.AnotherInformation.superclass.observerEmployeePk.call(this, {});
            if (this.myParams('employeePk')) {
                this.getCourseField().objectId(this.myParams('employeePk'));
            } else {
                this.getCourseField().disable();
                this.getCourseField().objectId(undefined);
            }
        },

        fields: function (cfg) {
            return [
                Ext._create('Ext.Panel', {
                    title: 'Curso',
                    items: [
                        this.getCourseField(),
                    ]
                }),
            ];
        },

        getCourseField: function (cfg) {
            if (!this._courseField)
                this._courseField = Ext._create('core.fields.RelatedRestfulField', {
                    region: 'north',
                    xtype: 'rest-relatedfield',
                    name: 'curso',
                    displayField: 'unicode',
                    allowBlank: false,
                    relatedname: 'servidor_set',
                    rest: 'rh.employee.Restful',
                    sourceRest: 'rh.curso.Restful',
                    width: '100%',
                    minHeight: 150,
                    height: 175,
                    border: false
                });

            return this._courseField;
        },
    }
);
