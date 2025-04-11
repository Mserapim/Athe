/**
 *
 **/
Ext._define('cif.educational.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getEducationalInstitution: function() {
        if(!this.educationalinstitution) {
            this.educationalinstitution = Ext._create('cif.educational.EducationalInstitutionGrid', {
                region: 'center',
            });
        }

        return this.educationalinstitution;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Instituição de Ensino'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getEducationalInstitution(),
                ]
            }
        );

        cif.educational.Manage.superclass.constructor.call(this, cfg);
    }
});
